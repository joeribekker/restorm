from decimal import Decimal

from restorm.clients.base import ClientMixin, BaseClient


JSON_LIBRARY_FOUND = True
# Prefer json over simplejson
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        JSON_LIBRARY_FOUND = False


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)

        from restorm.rest import RestObject
        if isinstance(o, RestObject):
            return o._obj

        super(CustomEncoder, self).default(o)


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
