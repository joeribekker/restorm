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


class JSONClientMixin(ClientMixin):
    MIME_TYPE = 'application/json'

    def create_request(self, uri, method, body=None, headers=None):
        if headers is None:
            headers = {}

        headers.update({
            'Accept': self.MIME_TYPE,
            'Content-Type': self.MIME_TYPE,
        })
        
        return super(JSONClientMixin, self).create_request(uri, method, body, headers)

    def create_response(self, response_headers, response_content, request):
        response = super(JSONClientMixin, self).create_response(response_headers, response_content, request)

        if 'Content-Type' in response and response['Content-Type'].startswith(self.MIME_TYPE):
            response.content = json.loads(response.content)
            
        return response

    def get(self, uri):
        return super(JSONClientMixin, self).get(uri)

    def post(self, uri, data):
        return super(JSONClientMixin, self).post(uri, json.dumps(data))

    def put(self, uri, data):
        return super(JSONClientMixin, self).put(uri, json.dumps(data))

    def delete(self, uri):
        return super(JSONClientMixin, self).delete(uri)


class JSONClient(BaseClient, JSONClientMixin):
    """
    Client that handles JSON requests and responses.
    """
    def __init__(self, *args, **kwargs):
        if not JSON_LIBRARY_FOUND:
            raise ImportError('Could not load any known JSON library.')
        super(JSONClient, self).__init__(*args, **kwargs)
