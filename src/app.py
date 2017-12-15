#!/usr/bin/env python
# encoding: utf-8

import logging
# Import the apistar modules we'll be using
from apistar import Include
from apistar.frameworks.asyncio import ASyncIOApp as App
from apistar.handlers import docs_urls, static_urls
# Import our local settings module
from settings import settings
# Import some local utilities whom's code we didn't want cluttering our app.py
from local_utils import print_routes, print_settings, print_components

# Import our components so we can register them with the app.
from aioclient import client
from backends import redis, asyncpg
import slackbot


logging.basicConfig(level=(settings.get('DEBUG') and logging.DEBUG) or logging.INFO)
logger = logging.getLogger()


routes = [
    Include('', slackbot.routes),
    Include('/static', static_urls),
    Include('/docs', docs_urls),
]


components = redis.components + asyncpg.components + slackbot.components + client.components


if settings.get('DEBUG'):
    logger.debug("Running in debug/development mode!!!")
    print_routes(routes)
    print_settings(settings)
    print_components(components)
    logger.debug("Building app now...")


app = App(
    routes=routes,
    settings=settings,
    components=components,
    commands=redis.commands + asyncpg.commands
)


if __name__ == '__main__':
    app.main()
