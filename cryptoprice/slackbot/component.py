import string
from pprint import pformat
import json
from apistar import Component, Settings, Response, reverse_url
from backends.redis import Redis
from backends.asyncpg import AsyncPgBackend
from aioclient.client import Client
from .crypto import CryptoWorld
import logging


logger = logging.getLogger(__name__)


# XXX(jeff) To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}


class CryptoBot(object):
    def __init__(self,
                 redis: Redis,
                 settings: Settings,
                 asyncpg: AsyncPgBackend,
                 client: Client) -> None:
        logger.debug("CryptoBot::__init__")

        self._config = settings.get('SLACK', {})
        self._asyncpg = asyncpg
        self._client = client

        self._name = self._config.get('BOT_NAME')
        self._emoji = ':robot_face:'
        self._verification = self._config.get('VERIFICATION_TOKEN')
        self._oauth = {
            'client_id': self._config.get('CLIENT_ID'),
            'client_secret': self._config.get('CLIENT_SECRET'),
            'scope': self._config.get('API_SCOPE'),
        }

        self._cw = CryptoWorld(redis, client)

        # Get the global async loop and have it run update to pre-heat
        # the cache of price data.
        #  loop = asyncio.get_event_loop()
        #  logger.debug("CryptoBot::__init__ loop: %s", loop)
        #  loop.run_until_complete(self._cw.update())
        #  logger.debug("CryptoBot::__init__ update done.")

    @property
    def api(self):
        return self._cw

    @property
    def name(self):
        return self._name

    @property
    def verification(self):
        return self._verification

    @property
    def emoji(self):
        return self._emoji

    @property
    def oauth(self):
        return self._oauth

    @property
    def config(self):
        return self._config.copy()

    async def get_team(self, team_id):
        data = await self._asyncpg.fetch("SELECT * FROM team WHERE slack_id = $1", team_id)

        logger.debug("GET TEAM %s : %s", team_id, data)
        return dict(data[0])

    def redir_uri(self, request=None):
        redir_base = self._config.get('BOT_OAUTH_REDIR')

        if not redir_base:
            (scheme, netloc, *_) = request.url.components
            redir_base = f'{scheme}://{netloc}'

        return f'{redir_base}{reverse_url("thanks")}'

    async def auth(self, code, redirect_uri):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.

        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token

        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint

        data = {
            'client_id': self.oauth["client_id"],
            'client_secret': self.oauth["client_secret"],
            'code': code,
            'redirect_uri': redirect_uri,
        }

        resp = await self._client.post('https://slack.com/api/oauth.access', data=data)
        logger.debug("OAuth auth response %s", resp)

        if resp.status != 200:
            resp.raise_for_status()
            # FYI: Will not always raise for status
            return ''

        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        r_data = await resp.json()
        team_id = r_data["team_id"]
        bot_token = r_data["bot"]["bot_access_token"]
        token = r_data["access_token"]
        name = r_data["team_name"]

        insert = await self._asyncpg.exec(
            """INSERT INTO team
                (slack_id, access_token, bot_access_token, name, auth)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (slack_id)
                DO UPDATE SET (access_token, bot_access_token, name, auth) =
                    (
                    EXCLUDED.access_token, EXCLUDED.bot_access_token,
                    EXCLUDED.name, EXCLUDED.auth
                    )
            """,
            team_id, token, bot_token, name, json.dumps(r_data))

        logger.debug("SlackBot oauth complete for team %s, %s", team_id, insert)

        return name

    async def send_price_message(self, team_id, user_id, channel_id, message):
        """
        Create and send a price quote users. Save the
        time stamp of this message on the message object for updating in the
        future.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event

        """
        logger.debug(
            'send_price_message channel: %s, username: %s, emoji: %s',
            channel_id, self.name, self.emoji
        )

        message = message.lower()
        logger.debug('MESSAGE: %s', message)
        parts = message.translate(str.maketrans('', '', string.punctuation)).split()
        logger.debug('MESSAGE PARTS: %s', parts)

        matched = await self._cw.fuzzy_match(parts)
        logger.debug('MATCHED: %s', matched)
        resp_str = '\n'.join([m.slack_str for m in matched])

        if not resp_str:
            logger.error("Empty price string generated!!! message: %s", message)

        team = await self.get_team(team_id)
        logger.debug("send_price team %s", pformat(team))

        headers = {
            'Authorization': f'Bearer {team["bot_access_token"]}',
            'Content-type': 'application/json',
        }

        data = {
            'as_user': True,
            'channel': channel_id,
            'username': self.name,
            'icon_emoji': self.emoji,
            'text': resp_str,
        }

        logger.debug("send_price sending message %s", resp_str)
        resp = await self._client.post(
                'https://slack.com/api/chat.postMessage',
                headers=headers,
                json=data,
        )

        #  logger.debug('send_price_message resp: %s', resp)

        if resp.status != 200:
            logger.error('problem while posting slack message. %s', resp)
            return ''

        return resp_str

    async def dispatch_event(self, event={}):
        event_type = event['event']['type']
        team_id = event["team_id"]

        if event_type == 'message':
            logger.debug('Message!')
            m_text = event['event'].get('text', '').lower()

            if 'price' in m_text:
                logger.debug('Price Message matched!')
                user_id = event["event"]["user"]
                await self.send_price_message(team_id, user_id, event["event"]["channel"], m_text)

                logger.debug('Pricing Message sent!')
                return {'message': 'Pricing!'}

        message = "I do not have an event handler for the %s" % event_type
        return Response(message, 200, headers={"X-Slack-No-Retry": '1'})


components = [Component(CryptoBot, init=CryptoBot)]
