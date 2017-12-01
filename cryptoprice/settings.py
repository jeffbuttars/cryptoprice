import logging
import json
from uuid import UUID
from pprint import pformat as pf
from apistar import environment, typesystem, http
from apistar.renderers import JSONRenderer


logger = logging.getLogger(__name__)


class SmarterJSONRenderer(JSONRenderer):
    def _default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)

        if hasattr(obj, 'isoformat'):
            return obj.isoformat()

        return json.JSONEncoder().encode(obj)

    def render(self, data: http.ResponseData) -> bytes:
        return json.dumps(data, default=self._default).encode('utf-8')


class Env(environment.Environment):
    properties = {
        'PYTHON_DEBUG': typesystem.boolean(default=False),
        'DEBUG': typesystem.boolean(default=False),
        'CLIENT_ID': typesystem.string(default='3430dd2a3e46404eb07c480759af0320'),
        'CLIENT_SECRET': typesystem.string(default='283832c3133849b19ae90b6b596ef933'),
        'REDIS_URL': typesystem.string(default='redis://127.0.0.1:6379/0'),
        'DATABASE_URL': typesystem.string(default=''),
        'VERIFICATION_TOKEN': typesystem.string(default='2514b2465e7448ecbdc55cff56b426b9'),
        'SLACK_BOT_TOKEN': typesystem.string(default='e544eb2e1cfb4abda385fb6e9b1e950e'),
        'SLACK_API_SCOPE': typesystem.string(default=''),
        'SLACK_BOT_NAME': typesystem.string(default=''),
        'SLACK_BOT_OAUTH_REDIR': typesystem.string(default=''),
    }


env = Env()


#  'URL': 'postgresql://cryptoprice:cryptoprice@localhost/cryptoprice'
settings = {
    'DATABASE': {
        'NAME': 'cryptoprice',
        'USER': 'cryptoprice',
        'PASSWORD': 'cryptoprice',
        'URL': env['DATABASE_URL'],

    },
    'REDIS': {
        'URL': env['REDIS_URL'],
        'MIN_POOL': 2,
        'MAX_POOL': 8,
    },
    'SLACK': {
        'CLIENT_ID': env['CLIENT_ID'],
        'CLIENT_SECRET': env['CLIENT_SECRET'],
        'VERIFICATION_TOKEN': env['VERIFICATION_TOKEN'],
        'BOT_TOKEN': env['SLACK_BOT_TOKEN'],
        'API_SCOPE': env['SLACK_API_SCOPE'],
        'BOT_NAME': env['SLACK_BOT_NAME'],
        'BOT_OAUTH_REDIR': env['SLACK_BOT_OAUTH_REDIR'],
    },
    'TEMPLATES': {
        'ROOT_DIR': ['index/templates', 'slackbot/templates'],
        'PACKAGE_DIRS': ['apistar'],
    },
    'RENDERERS': [SmarterJSONRenderer()],
    'DEBUG': env['DEBUG'] or env['PYTHON_DEBUG']
}

logger.debug("settings %s", pf(settings))
