from urllib.parse import urlparse
import subprocess
import asyncio
import aioredis
from apistar import Command, Component, Settings
import logging


logger = logging.getLogger(__name__)


class Redis(object):
    """
    Redis backend
    """
    def __init__(self, settings: Settings) -> None:
        """
        Initialize the Redis connection pool and provide a simple
        interface to Redis connections.
        NOTE: The connection pool is established and tested in a blocking fashion.

        XXX(jeff) Update settings to be more flexible and parse
        out the URL if needed for the cli.
        """
        logger.debug('Redis::__init__:')

        self._config = settings.get('REDIS', {})
        self._pool = None
        self._url = self._config.get('URL')
        self._min_pool = self._config.get('MIN_POOL', 1)
        self._max_pool = self._config.get('MAX_POOL', 8)

    @property
    async def pool(self):
        if not self._pool:
            return await self._connect()

        return self._pool

    async def _connect(self):
        try:
            logger.debug('Creating pool...')

            address, config = self._build_config()
            self._pool = await aioredis.create_pool(address, **config)
            logger.debug('Connection pool %s', self._pool)

            ping = await self._pool.execute('ping')
            logger.debug('Connection ping %s', ping)
        except Exception as e:
            logger.error("Redis connection error: %s", e)
            raise

        return self._pool

    def _build_config(self):
        url = urlparse(self._url)

        # Remove query strings.
        path = url.path[1:]
        path = path.split('?', 2)[0]

        config = {
            "db": int(path or 0),
            "password": url.password or None,
            'minsize': self._min_pool,
            'maxsize': self._max_pool,
        }

        address = (url.hostname or "localhost", int(url.port or 6379))

        return (address, config)

    async def exec(self, *args, **kwargs):
        logger.debug('Redis::exec: %s', ("%s %s" % (args, kwargs))[:128])

        for arg in args:
            logger.debug('Redis::exec: %s', ("%s" % (arg,))[:32])

        pool = await self.pool

        try:
            return await pool.execute(*args, **kwargs)
        except Exception as e:
            logger.error("Redis exec error: %s", e)
            raise

    async def conn_info(self):
        logger.debug('Redis::conn_info')
        pool = await self.pool

        with await pool as conn:
            return {
                'address': conn.address,
                'db': conn.db,
            }

    @property
    def config(self):
        """
        Return a copy of the current Redis config.
        """
        return self._config.copy()


def redis_cli(redis_cache: Redis):
    """
    Run the Redis cli with the project Redis connection settings
    """
    loop = asyncio.get_event_loop()
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
