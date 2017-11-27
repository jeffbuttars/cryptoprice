import string
from slackclient import SlackClient
from apistar import Component, Settings, Response
from backends.redis import Redis
from .crypto import CryptoWorld
import logging


logger = logging.getLogger(__name__)


# XXX(jeff) To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}


class CryptoBot(object):
    def __init__(self, redis: Redis, settings: Settings, emoji=':robot_face:') -> None:
        self._name = settings.get('SLACK', {}).get('BOT_NAME')
        self._verification = settings.get('SLACK', {}).get('VERIFICATION_TOKEN')
        self._oauth = {
            'client_id': settings.get('SLACK', {}).get('CLIENT_ID'),
            'client_secret': settings.get('SLACK', {}).get('CLIENT_SECRET'),
            'scope': settings.get('SLACK', {}).get('API_SCOPE'),
        }

        self._client = SlackClient(settings.get('SLACK', {}).get('BOT_TOKEN'))

        self._cw = CryptoWorld(redis)
        self._cw.update()

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
    def client(self):
        return self._client

    def auth(self, code):
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
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                 auth_response["bot"]["bot_access_token"]}

        # Then we'll reconnect to the Slack Client with the correct team's
        # bot token
        self.client = SlackClient(authed_teams[team_id]["bot_token"])

    def send_price_message(self, team_id, user_id, channel_id, message):
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
        parts = message.translate(str.maketrans('', '', string.punctuation)).split()

        matched = self._cw.fuzzy_match(parts)
        logger.debug('MATCHED: %s', matched)
        resp_str = '\n'.join([m.slack_str for m in matched])

        resp = self.client.api_call(
            'chat.postMessage',
            as_user=True,
            channel=channel_id,
            username=self.name,
            icon_emoji=self.emoji,
            text=resp_str,
        )

        logger.debug('send_price_message resp: %s', resp)

    def dispatch_event(self, event={}):
        event_type = event['event']['type']
        team_id = event["team_id"]

        if event_type == 'message':
            print('Message!')
            m_text = event['event'].get('text', '').lower()
            if 'price' in m_text:
                logger.debug('Price Message!')
                user_id = event["event"]["user"]
                self.send_price_message(team_id, user_id, event["event"]["channel"], m_text)

                return {'message': 'Pricing!'}

        message = "I do not have an event handler for the %s" % event_type
        return Response(message, 200, headers={"X-Slack-No-Retry": '1'})


components = [Component(CryptoBot)]
