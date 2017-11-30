import subprocess
import asyncio
import aioredis
from apistar import Command, Component, Settings
import logging


logger = logging.getLogger(__name__)
loop = asyncio.get_event_loop()


class Redis(object):
    """
    Redis backend
    """
    def __init__(self, settings: Settings) -> None:
        logger.debug('Redis::__init__:')

        c_key = 'REDIS'
        if not settings.get(c_key, {}).get('URL'):
            c_key = 'CACHE'

        self._config = settings.get(c_key, {})

        self._url = self._config.get('URL')
        self._min_pool = self._config.get('MIN_POOL', 1)
        self._max_pool = self._config.get('MAX_POOL', 8)

        self._pool = loop.run_until_complete(aioredis.create_pool(self._url))

        logger.debug('Redis::__init__: pool %s', self._pool)

    async def exec(self, *args, **kwargs):
        logger.debug('Redis::exec: %s %s', args, kwargs)
        return await self._pool.execute(*args, **kwargs)

    async def conn_info(self):
        logger.debug('Redis::conn_info')

        with await self._pool as conn:
            return {
                'address': conn.address,
                'db': conn.db,
            }

    @property
    def config(self):
        return self._config.copy()

    @property
    def url(self):
        print('Redis::url', self._url)
        return self._url

    @property
    def kwargs(self):
        print('Redis::kwargs', self._pool.connection_kwargs)
        return self._pool.connection_kwargs


def redis_cli(redis_cache: Redis):
    """
    Run the Redis cli with the project Redis connection settings
    """
    conn_info = loop.run_until_complete(redis_cache.conn_info())

    args = ['redis-cli', '-n', f"{conn_info.get('db', 0)}"]

    if isinstance(conn_info['address'], str):
        args += ['-s', conn_info['address']]
    else:
        args += ['-h', conn_info['address'][0], '-p', str(conn_info['address'][1])]

    if redis_cache.config.get('password'):
        args += ['-a', redis_cache.config.get('password')]

    logger.debug('REDIS CLI: %s', ' '.join(args))
    subprocess.call(args)


components = [
    Component(Redis, init=Redis),
]

commands = [
    Command('redis_cli', redis_cli)
]
