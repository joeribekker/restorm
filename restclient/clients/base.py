import urlparse
import httplib2

try:
    import json
except ImportError:
    # Python 2.5 compatability.
    import simplejson as json


class Request(dict):
    def __init__(self, uri, method, body=None, headers=None):
        super(Request, self).__init__()

        self._uri = uri
        self._method = method
        self._body = body

        if headers is None:
            headers = {}

        self._headers = headers

        self.update(dict([(k.title().replace('_', '-'), v) for k, v in headers.items()]))
    
    @property
    def headers(self):
        """
        Return the actual headers.
        """
        return self._headers 
    
    @property
    def uri(self):
        return self._uri
    
    @property
    def method(self):
        return self._method
    
    @property
    def body(self):
        return self._body


class Response(dict):
    def __init__(self, client, response_headers, response_content, request):
        super(Response, self).__init__()

        self.client = client
        self.headers = response_headers
        self.content = response_content
        self.request = request

        # Make headers consistently accessible. 
        self.update(dict([(k.title().replace('_', '-'), v) for k, v in response_headers.items()]))
        
        # Set status code on its own property.
        self.status_code = int(self.pop('Status'))


class ClientMixin(object):
    def create_request(self, uri, method, body, headers):
        return Request(uri, method, body, headers)
    
    def create_response(self, response_headers, response_content, request):
        return Response(self, response_headers, response_content, request)

    def get(self, uri):
        return self.request(uri, 'GET')

    def post(self, uri, data):
        return self.request(uri, 'POST', data)

    def put(self, uri, data):
        return self.request(uri, 'PUT', data)

    def delete(self, uri):
        return self.request(uri, 'DELETE')


class BaseClient(httplib2.Http):
    """
    Simple REST client based on ``httplib2.Http``.
    """
    def request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
        # Create request.
        request = self.create_request(uri, method, body, headers)

        # Perform an HTTP-request with ``httplib2``.
        response_headers, response_content = super(BaseClient, self).request(request.uri, request.method, request.body, request, redirections, connection_type)
        
        # Create response.
        return self.create_response(response_headers, response_content, request)


class Client(BaseClient, ClientMixin):
    pass