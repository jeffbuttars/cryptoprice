import redis
from apistar import Component, Settings


class RedisConn(object):
    def __init__(self, settings: Settings) -> None:
        self._url = settings.get('CACHE', {}).get('URL')
        self._rc = redis.Redis.from_url(self._url)

    @property
    def redis(self):
        return self._rc

    @property
    def url(self):
        return self._url


RedisConnection = Component(RedisConn)
