from restclient.rest import RestObject
from restclient.clients.base import Client, Response


try:
    import json
except ImportError:
    # Python 2.5 compatability.
    import simplejson as json


class JSONResponse(Response):
    def __init__(self, client, response, request):
        super(Response, self).__init__(client, response, request)

        # Replace the content with Python.
        if 'Content-Type' in self and self['Content-Type'].startswith('application/json'):
            self.content = json.loads(self.content, object_hook=RestObject)
        else:
            raise ValueError

            
class JSONClient(Client):
    """
    Client that handles JSON requests and responses.
    """
    def request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
        if headers is None:
            headers = {}

        headers.update({
            'Content-Type': 'application/json',
        })

        response = super(Client, self).request(uri, method, body, headers, redirections, connection_type)
        
        return Response(self, response, uri, method, headers)

    def get(self, uri, data=None):
        return self.get(uri, data)

    def post(self, uri, data):
        return self.post(uri, json.dumps(data))

    def put(self, uri, data):
        return self.put(uri, json.dumps(data))

    def delete(self, uri):
        return self.delete(uri)