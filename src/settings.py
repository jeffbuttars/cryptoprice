"""
The cryptoprice settings mostly maps environmental values to settings names and values
with defaults provided.

Cryptoprice also uses a customized JSONRenderer, so import that and set it as our projects
:code:`RENDERER`.
"""

import logging
from apistar import environment, typesystem
from local_utils.renderer import JSONRenderer


logger = logging.getLogger(__name__)


class Env(environment.Environment):
    """
    Simple mapping from environment settings.
    """
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
    'RENDERERS': [JSONRenderer()],
    'DEBUG': env['DEBUG'] or env['PYTHON_DEBUG']
}
"""
The all mighty settings object
"""
