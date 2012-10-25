from restclient.rest import RestObject
from restclient.clients.base import ClientMixin, BaseClient


try:
    import json
except ImportError:
    # Python 2.5 compatability.
    import simplejson as json


class JSONClientMixin(ClientMixin):

    def create_request(self, uri, method, body=None, headers=None):
        if headers is None:
            headers = {}

        headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        
        return super(JSONClientMixin, self).create_request(uri, method, body, headers)

    def create_response(self, response_headers, response_content, request):
        response = super(JSONClientMixin, self).create_response(response_headers, response_content, request)

        if 'Content-Type' in response and response['Content-Type'].startswith('application/json'):
            response.content = json.loads(response.content, object_hook=RestObject)
            
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
    pass