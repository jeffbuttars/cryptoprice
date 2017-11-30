import logging
from apistar import Component
import aiohttp


logger = logging.getLogger(__name__)


def mergeargs(func):
    async def helper(self, *args, **kwargs):
        if self._headers:
            hdrs = self._headers.copy()
            hdrs.update(kwargs.get('headers', {}))
            kwargs['headers'] = hdrs

        return await func(self, *args, **kwargs)

    return helper


class Client(object):
    def __init__(self, headers={}):
        self._session = aiohttp.ClientSession()
        logger.debug("AIOClient init, session: %s", self._session)
        self._headers = headers

    @classmethod
    def set_headers(cls, headers={}):
        # A funny factory to get an instance with preset headers that are included
        # in every requests. This makes it easy to get a new instance while keeping
        # it's usage with the Component pattern easy.
        return cls(headers=headers)

    @mergeargs
    async def get(self, *args, **kwargs):
        logger.debug("AIOClient get")
        resp = await self._session.get(*args, **kwargs)

        logger.debug("AIOClient get resp: %s", resp)
        logger.debug("AIOClient get resp: %s", dir(resp))

        return resp

    @mergeargs
    async def post(self, *args, **kwargs):
        logger.debug("AIOClient post")
        resp = await self._session.post(*args, **kwargs)

        logger.debug("AIOClient post resp: %s", resp)
        logger.debug("AIOClient post resp: %s", dir(resp))

        return resp


components = [
    Component(Client, init=Client)
]
