import json
from uuid import UUID
from apistar.renderers import JSONRenderer as BaseJSONRenderer
from apistar import http


class JSONRenderer(BaseJSONRenderer):
    """
    An extended JSONRenderer that will serialize datetime objects to their string ISO format
    and UUID instances to their string value.
    """
    def _default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)

        if hasattr(obj, 'isoformat'):
            return obj.isoformat()

        return json.JSONEncoder().encode(obj)

    def render(self, data: http.ResponseData) -> bytes:
        return json.dumps(data, default=self._default).encode('utf-8')
