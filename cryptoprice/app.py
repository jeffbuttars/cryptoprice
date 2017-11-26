#!/usr/bin/env python
# encoding: utf-8

from pprint import pformat as pf
from apistar import Include
from apistar.frameworks.asyncio import ASyncIOApp as App
from apistar.handlers import docs_urls, static_urls
from index.index import routes as index_routes
import logging

# Set up the logger
logger = logging.getLogger(__name__)
# Use a console handler, set it to debug by default
logger_ch = logging.StreamHandler()
logger.setLevel(logging.DEBUG)
#  log_formatter = logging.Formatter(('%(levelname)s: %(asctime)s %(processName)s:%(process)d'
#                                     ' %(filename)s:%(lineno)s %(module)s::%(funcName)s()'
#                                     ' -- %(message)s'))
#  logger_ch.setFormatter(log_formatter)
logger.addHandler(logger_ch)


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
    Include('/', index_routes),
    Include('/static', static_urls),
    Include('/docs', docs_urls),
]

settings = {
    'TEMPLATES': {
        'ROOT_DIR': ['index/templates'],
        'PACKAGE_DIRS': ['apistar'],
    },
}
logger.debug("settings %s", pf(settings))

app = App(routes=routes, settings=settings)


if __name__ == '__main__':
    app.main()