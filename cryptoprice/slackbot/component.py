from apistar import Component
from backends.redis import Redis
from .crypto import CryptoWorld


class CryptoAPI(object):
    def __init__(self, redis: Redis) -> None:
        self._cw = CryptoWorld(redis)
        self._cw.update()

    @property
    def api(self):
        return self._cw


components = [Component(CryptoAPI)]
