#!/usr/bin/env python
# encoding: utf-8

"""

This is the entry point of the application and is also the highest level of orchestration for your
`API Star <https://github.com/encode/apistar>`_ app. This is where we import the libraries and app
specific modules that we'll use to construct the :code:`App` instance.


In this application, we have several custom components we need to register with the :code:`App` and
our settings module for use by the :code:`App`. We also setup a basic root logger here.
If debug/dev mode is detected then we'll log the app specific routes,
settings and components at start up.

Logger Setup
--------------------

We use a basic a root logger that will set the level to :code:`DEBUG` if the settings
have :code:`DEBUG` set to something truthy and :code:`INFO` otherwise.

Route Setup
-------------------

We :code:`Include` our project routes from :doc:`slackbot/index` and then routes from
`API Star <https://github.com/encode/apistar>`_ itself to include it's static and docs routes.


App Instantiation
-----------------

We instantiate the :code:`App` instance with

    * Routes
        * Our project routes and the `API Star <https://github.com/encode/apistar>`_ routes we use.
    * Settings
        * Our project settings instance from :doc:`settings`
    * Components
        * Our project's custom components to be registered:
            * :doc:`aioclient/index`
            * :doc:`backends/asyncpg`
            * :doc:`backends/redis`
            * :doc:`slackbot/component`
    * Commands
        * Our project's custom commands to be registered:
            * :doc:`backends/asyncpg`
            * :doc:`backends/redis`

::

    app = App(
        routes=routes,
        settings=settings,
        components=components,
        commands=redis.commands + asyncpg.commands
    )
"""


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


# In DEBUG/DEV environment dump more info to the console/logger
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
