from apistar import Component
from redis_component import RedisConnection
from .crypto import CryptoWorld


class Cryptoapi(object):
    def __init__(self, rc: RedisConnection) -> None:
        self._rc = rc.redis
        self._cw = CryptoWorld(self._rc.redis)
        self._cw.update()

    @property
    def api(self):
        return self._cw


CryptoAPI = Component(Cryptoapi)
