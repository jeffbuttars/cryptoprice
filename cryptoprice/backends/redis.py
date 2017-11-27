import subprocess
from redis import Redis
from apistar import Command, Component, Settings


class RedisBackend(object):
    """
    Redis backend
    """
    def __init__(self, settings: Settings) -> None:
        print('RedisBackend::__init__', settings)
        self._url = settings.get('REDIS', {}).get('URL')
        if not self._url:
            self._url = settings.get('CACHE', {}).get('URL')

        self._session = Redis.from_url(self._url)

    @property
    def session(self):
        print('RedisBackend::sessin', self._session)
        return self._session

    @property
    def url(self):
        print('RedisBackend::url', self._url)
        return self._url

    @property
    def kwargs(self):
        print('RedisBackend::kwargs', self._session.connection_pool.connection_kwargs)
        return self._session.connection_pool.connection_kwargs


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
    Component(RedisBackend),
    Component(Redis, init=get_session, preload=False),
]

commands = [
    Command('redis_cli', redis_cli)
]
