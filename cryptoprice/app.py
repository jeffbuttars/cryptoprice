#!/usr/bin/env python
# encoding: utf-8

import logging
from apistar import Include
from apistar.frameworks.asyncio import ASyncIOApp as App
from apistar.handlers import docs_urls, static_urls
from settings import settings
from local_utils import print_routes, print_settings
from index.index import routes as index_routes
from backends import redis
import slackbot


logging.basicConfig(level=settings.get('DEBUG') and logging.DEBUG)
logger = logging.getLogger()


# Set up the logger
# Use a console handler, set it to debug by default
#  logger_ch = logging.StreamHandler()
#  logger_ch.setLevel(() or logging.INFO)
#  log_formatter = logging.Formatter(('%(levelname)s: %(asctime)s %(processName)s:%(process)d'
#                                     ' %(filename)s:%(lineno)s %(module)s::%(funcName)s()'
#                                     ' -- %(message)s'))
#  logger_ch.setFormatter(log_formatter)
#  logger.addHandler(logger_ch)


#  async def welcome(
#      username: str='',
#      request: http.Request=None,
#      params: http.QueryParams={},
#      headers: http.Headers={},
#  ):
#      rstr = '%s : %s' % (request, dir(request))
#      pstr = '%s' % (params,)
#      hstr = '%s' % (headers,)

#      logger.debug("Request: %s", rstr)
#      logger.debug("Params: %s", pstr)
#      logger.debug("Headers: %s", hstr)

#      if username is None:
#          return {
#              'message': 'Welcome to API Star!',
#              'request': rstr,
#          }

#      return {
#          'message': 'Welcome to API Star, %s!' % username,
#          'request': rstr,
#      }

routes = [
    Include('', index_routes),
    Include('', slackbot.routes),
    Include('/static', static_urls),
    Include('/docs', docs_urls),
]


components = slackbot.components + redis.components


if settings.get('DEBUG'):
    print("Running in debug/development mode!!!")
    print_routes(routes)
    print_settings(settings)
    logger.debug("Components: %s", components)
    print("Building app now...")


app = App(
    routes=routes,
    settings=settings,
    components=components,
    commands=redis.commands
)


if __name__ == '__main__':
    app.main()
