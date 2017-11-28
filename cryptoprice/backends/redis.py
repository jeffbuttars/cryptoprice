import subprocess
import redis
from redis.exceptions import ConnectionError
from apistar import Command, Component, Settings
import logging


logger = logging.getLogger(__name__)
Redis = redis.Redis


class RedisBackend(object):
    """
    Redis backend
    """
    def __init__(self, settings: Settings) -> None:
        logger.debug('RedisBackend::__init__:')

        self._url = settings.get('REDIS', {}).get('URL')

        if not self._url:
            self._url = settings.get('CACHE', {}).get('URL')

        self._pool = redis.ConnectionPool.from_url(self._url)

        try:
            session = Redis(connection_pool=self._pool)
            resp = session.ping()
            logger.debug("Redis ping: %s", resp)
        except ConnectionError as e:
            logger.error("Redis Connection Error: %s", e)

    @property
    def session(self):
        _session = Redis(connection_pool=self._pool)
        print('RedisBackend::session', _session)
        return _session

    @property
    def url(self):
        print('RedisBackend::url', self._url)
        return self._url

    @property
    def kwargs(self):
        print('RedisBackend::kwargs', self._pool.connection_kwargs)
        return self._pool.connection_kwargs


def get_session(backend: RedisBackend) -> Redis:
    return backend.session


def redis_cli(redis: RedisBackend):
    """
    Run the Redis cli with the project Redis connection settings
    """
    kwargs = redis.kwargs
    {'db': 0, 'host': '127.0.0.1', 'password': None, 'port': 6379}

    db = ['-n', f"{kwargs.get('db', 0)}"]
    host = ['-h', kwargs.get('host', '127.0.0.1')]
    port = ['-p', f"{kwargs.get('port', 6379)}"]
    password = []

    if kwargs.get('password'):
        password += ['-a', kwargs.get('password')]

    print('REDIS CLI:', ['redis-cli'] + host + password + port + db)

    subprocess.call(
        ['redis-cli'] + host + password + port + db
    )


components = [
    Component(RedisBackend, init=RedisBackend),
    Component(Redis, init=get_session, preload=False),
]

commands = [
    Command('redis_cli', redis_cli)
]
