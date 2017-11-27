import logging
from pprint import pformat as pf
from apistar import environment, typesystem


logger = logging.getLogger(__name__)


class Env(environment.Environment):
    properties = {
        'PYTHON_DEBUG': typesystem.boolean(default=False),
        'DEBUG': typesystem.boolean(default=False),
        'CLIENT_ID': typesystem.string(default='3430dd2a3e46404eb07c480759af0320'),
        'CLIENT_SECRET': typesystem.string(default='283832c3133849b19ae90b6b596ef933'),
        'REDIS_URL': typesystem.string(default='redis://127.0.0.1:6379/0'),
        'VERIFICATION_TOKEN': typesystem.string(default='2514b2465e7448ecbdc55cff56b426b9'),
        'SLACK_BOT_TOKEN': typesystem.string(default='e544eb2e1cfb4abda385fb6e9b1e950e'),
        'SLACK_API_SCOPE': typesystem.string(default=''),
        'SLACK_BOT_NAME': typesystem.string(default=''),
    }


env = Env()


settings = {
    'CACHE': {
        'URL': env['REDIS_URL'],
    },
    'SLACK': {
        'CLIENT_ID': env['CLIENT_ID'],
        'CLIENT_SECRET': env['CLIENT_SECRET'],
        'VERIFICATION_TOKEN': env['VERIFICATION_TOKEN'],
        'BOT_TOKEN': env['SLACK_BOT_TOKEN'],
        'API_SCOPE': env['SLACK_API_SCOPE'],
        'BOT_NAME': env['SLACK_BOT_NAME'],
    },
    'TEMPLATES': {
        'ROOT_DIR': ['index/templates', 'slackbot/templates'],
        'PACKAGE_DIRS': ['apistar'],
    },
    'DEBUG': env['DEBUG'] or env['PYTHON_DEBUG']
}

logger.debug("settings %s", pf(settings))
