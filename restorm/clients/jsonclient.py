from decimal import Decimal
from restorm.clients.base import ClientMixin, BaseClient


JSON_LIBRARY_FOUND = True
try:
    import json
except ImportError:
    # Python 2.5 compatability.
    try:
        import simplejson as json
    except ImportError:
        JSON_LIBRARY_FOUND = False


class DecimalEncoder(json.JSONEncoder):
    def _iterencode(self, o, markers=None):
        if isinstance(o, Decimal):
            return (str(o) for o in [o])
        return super(DecimalEncoder, self)._iterencode(o, markers)


class JSONClientMixin(ClientMixin):
    MIME_TYPE = 'application/json'

    def serialize(self, data):
        if data is None:
            return ''
        return json.dumps(data, cls=DecimalEncoder)
    
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
