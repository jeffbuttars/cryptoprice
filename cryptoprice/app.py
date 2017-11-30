#!/usr/bin/env python
# encoding: utf-8

import logging
from apistar import Include
from apistar.frameworks.asyncio import ASyncIOApp as App
from apistar.handlers import docs_urls, static_urls
from settings import settings
from local_utils import print_routes, print_settings, print_components
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
    print("Running in debug/development mode!!!")
    print_routes(routes)
    print_settings(settings)
    print_components(components)
    print("Building app now...")


app = App(
    routes=routes,
    settings=settings,
    components=components,
    commands=redis.commands + asyncpg.commands
)


if __name__ == '__main__':
    app.main()
