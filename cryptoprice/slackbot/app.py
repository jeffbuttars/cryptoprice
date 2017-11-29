import logging
from pprint import pformat
from asyncpg import Connection
from apistar import http, Route, Settings, Response, render_template, annotate, reverse_url
from apistar.renderers import HTMLRenderer
from .component import CryptoBot


logger = logging.getLogger(__name__)


@annotate(renderers=[HTMLRenderer()])
async def install(crypto_bot: CryptoBot):
    """This route renders the installation page with 'Add to Slack' button."""
    # Since we've set the client ID and scope on our Bot object, we can change
    # them more easily while we're developing our app.
    logger.debug("SLACK EVENT install")

    # Our template is using the Jinja templating language to dynamically pass
    # our client id and scope
    return render_template(
        "install.html",
        client_id=crypto_bot.oauth['client_id'],
        scope=crypto_bot.oauth['scope'],
        redirect_uri=reverse_url('thanks'),
    )


async def listening(slack_event: http.RequestData, crypto_bot: CryptoBot, settings: Settings):
    """
    The Slack API event handler.
    Also handles the Slack challenge request.
    """
    print("SLACK EVENT listening: %s" % pformat(slack_event))
    slack_event = slack_event or {}
    logger.debug("SLACK EVENT listening: %s", pformat(slack_event))
    logger.debug("SLACK EVENT api: %s", crypto_bot)

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return {'challenge': slack_event['challenge']}

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if crypto_bot.verification != slack_event.get("token"):
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.

        headers = {}
        if settings.get('DEBUG'):
            headers['X-Slack-No-Retry'] = '1'

        return Response(
            'Invalid Slack verification token',
            status=403,
            headers=headers
        )

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        return crypto_bot.dispatch_event(slack_event)
        #  event_type = slack_event["event"]["type"]

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    headers = {}
    if settings.get('DEBUG'):
        headers['X-Slack-No-Retry'] = '1'

    return Response(
        "[NO EVENT IN SLACK REQUEST] These are not the droids you're looking for.",
        status=404,
        headers=headers
    )


@annotate(renderers=[HTMLRenderer()])
async def thanks(code: str, crypto_bot: CryptoBot):
    """
    This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    logger.debug("SLACK EVENT thanks: %s", code)
    # The bot's auth method to handles exchanging the code for an OAuth token
    try:
        crypto_bot.auth(code)
    except Exception as e:
        return Response('Unable to authenticate!: %s' % e, status=500)

    return render_template("thanks.html", code=code)


async def dbtest(self, connection: Connection):
    conn_str = ''
    data = None

    async with connection as conn:
        conn_str = dir(conn)
        data = await conn.fetch('SELECT * FROM team')

    return {
        'message': 'dbtest',
        'connection': dir(connection),
        'conn': conn_str,
        'data': data,
    }


routes = [
    Route('/listening', 'POST', listening),
    Route('/thanks', 'GET', thanks),
    Route('/install', 'GET', install),
    Route('/dbtest', 'GET', dbtest),
]
