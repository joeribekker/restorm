import httplib2

try:
    import json
except ImportError:
    # Python 2.5 compatability.
    import simplejson as json


class Response(dict):
    def __init__(self, client, response, request_uri, request_method, request_headers):
        super(Response, self).__init__()

        self.headers = response[0]
        self.content = response[1]
        self.client = client
        
        # Create request object.
        request = {
            'PATH_INFO': request_uri,
            'REQUEST_METHOD': request_method,
            'QUERY_STRING': '',
        }
        request.update(dict([(k.upper().replace('-', '_'), v) for k, v in request_headers.items()]))

        self.request = request

        # Make headers consistently accessible. 
        self.update(dict([(k.title(), v) for k, v in response[0].items()]))
        
        # Set status code on its own property.
        self.status_code = int(self.pop('Status'))

            
class Client(httplib2.Http):
    """
    Simple REST client based on ``httplib2.Http``.
    
    This client behaves similar to the one provided by Django's testsuite.
    """
    def request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
        raw_response = super(Client, self).request(uri, method, body, headers, redirections, connection_type)
        
        return Response(self, raw_response, uri, method, headers)

    def get(self, uri, data=None):
        if data is None:
            data = {}
        return self.request(uri, 'GET')#, data)

    def post(self, uri, data):
        return self.request(uri, 'POST', data)

    def put(self, uri, data):
        return self.request(uri, 'PUT', data)

    def delete(self, uri):
        return self.request(uri, 'DELETE')
