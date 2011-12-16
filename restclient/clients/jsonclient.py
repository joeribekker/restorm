from restclient.rest import RestObject
from restclient.clients.base import Client, Response


try:
    import json
except ImportError:
    # Python 2.5 compatability.
    import simplejson as json


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

        response = super(JSONClient, self).request(uri, method, body, headers, redirections, connection_type)
        
        response.content = json.loads(response.content)

        return response

    def get(self, uri, data=None):
        return super(JSONClient, self).get(uri, data)

    def post(self, uri, data):
        return super(JSONClient, self).post(uri, json.dumps(data))

    def put(self, uri, data):
        return super(JSONClient, self).put(uri, json.dumps(data))

    def delete(self, uri):
        return super(JSONClient, self).delete(uri)