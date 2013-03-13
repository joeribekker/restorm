from decimal import Decimal

from restorm.clients.base import ClientMixin, BaseClient


JSON_LIBRARY_FOUND = True
try:
    # Prefer simplejson over standard library.
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        JSON_LIBRARY_FOUND = False


class CustomEncoder(json.JSONEncoder):
    def encode(self, o):
        from restorm.rest import RestObject
        if isinstance(o, RestObject):
            o = o._obj
        return super(CustomEncoder, self).encode(o)

    def _iterencode(self, o, markers=None):
        if isinstance(o, Decimal):
            return (str(o) for o in [o])
        return super(CustomEncoder, self)._iterencode(o, markers)


class JSONClientMixin(ClientMixin):
    MIME_TYPE = 'application/json'

    def serialize(self, data):
        if data is None:
            return ''
        return json.dumps(data, cls=CustomEncoder)
    
    def deserialize(self, data):
        if data == '':
            return None
        return json.loads(data, parse_float=Decimal)


class JSONClient(BaseClient, JSONClientMixin):
    """
    Client that handles JSON requests and responses.
    """
    def __init__(self, *args, **kwargs):
        if not JSON_LIBRARY_FOUND:
            raise ImportError('Could not load any known JSON library.')
        super(JSONClient, self).__init__(*args, **kwargs)
