import logging
from pprint import pformat
from apistar import http, Route, Settings, Response
from .component import CryptoAPI


logger = logging.getLogger(__name__)


async def listening(slack_event: http.RequestData, crypto_api: CryptoAPI, settings: Settings):
    logger.debug("SLACK EVENT listening: %s", pformat(slack_event))
    logger.debug("SLACK EVENT api: %s", crypto_api)

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
    if settings.get('SLACK', {}).get('VERIFICATION_TOKEN') != slack_event.get("token"):
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        return Response(
            'Invalid Slack verification token',
            statue=403,
            headers={"X-Slack-No-Retry": 1}
        )


routes = [
    Route('/listening', 'GET', listening, name='listening-get'),
    Route('/listening', 'POST', listening, name='listening-post'),
]
