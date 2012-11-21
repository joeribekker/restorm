import SimpleHTTPServer
import urlparse
import os

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from restorm.clients.base import ClientMixin


class MockResponse(list):
    """
    Main class for mocked responses. Headers can be provided as dict. The 
    content is simply returned as response and is usually a string but can be
    any type of object.
    """
    def __init__(self, headers, content):
        self.headers = headers
        self.content = content

        super(MockResponse, self).__init__((headers, content))


class StringResponse(MockResponse):
    """
    A response comming from a string.

    **Example**

    >>> desired_response = StringResponse({'Status': 200}, '{}')
    """
    def __init__(self, headers, content):
        super(StringResponse, self).__init__(headers, unicode(content))


class FileResponse(MockResponse):
    """
    A response comming from an absolute file path.

    **Example**
    
    >>> desired_response = FileResponse({'Status': 200}, 'response.json')
    """
    def __init__(self, headers, filepath):
        if not os.path.isfile(filepath):
            raise ValueError('Cannot find file "%s".' % filepath)

        f = open(filepath)
        content = f.read()
        f.close()
        
        super(FileResponse, self).__init__(headers, content)


class BaseMockClient(object):
    root_uri = ''

    def __init__(self, *args, **kwargs):
        self.responses = kwargs.pop('responses', [])
        if 'root_uri' in kwargs:
            self.root_uri = kwargs.pop('root_uri')

        self._response_index = 0
    
    def request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
        if self._response_index >= len(self.responses):
            raise RuntimeError('Ran out of responses when requesting: %s' % uri)

        if not uri.startswith(self.root_uri):
            urlparse.urljoin(self.root_uri, uri)

        request = self.create_request(uri, method, body, headers)

        # Get current queued mock response.
        response = self.responses[self._response_index]

        # Set minimal response headers.
        response_headers = {
            'Server': 'Mock Client',
            'Status': 0,
        }
        response_headers.update(response.headers)
        
        return self.create_response(response_headers, response.content, request)


class MockClient(BaseMockClient, ClientMixin):
    """
    A mock client, emulating the rest client. The client returns predefined 
    responses.
    
    You can add fake response as either a StringResponse or a FileResponse. The
    first argument of these classes should always be a dict of headers, the 
    second argument is the content as string or file path respectively.
    
    **Example**

    >>> desired_response = StringResponse({'Status': 200}, '{}')
    >>> client = MockClient('http://mockserver/', responses=[desired_response,])
    >>> response = client.get('/')
    >>> response.content
    u'{}'
    >>> response.status_code
    200
    """
    pass


class BaseMockApiClient(object):
    root_uri = ''
    
    def __init__(self, *args, **kwargs):
        self.responses = kwargs.pop('responses', {})
        if 'root_uri' in kwargs:
            self.root_uri = kwargs.pop('root_uri')

    def get_response_from_request(self, request):
        """
        You may override this method to implement your own response logic based
        on given request. You can even modify the ``self.responses`` based on 
        some POST, PUT or DELETE request.
        
        This is the only method that looks at ``self.responses``. Therefore,
        overriding this method also allows you to create a custom format for
        this container variable.
        """
        
        # Get mock response for URI (look for full URI and path URI).
        response_methods = self.responses.get(request.uri) or self.responses.get(request.uri[len(self.root_uri):])
        
        # If the URI is not found, return a 404.
        if response_methods is None:
            response_headers, response_content = {'Status': 404}, 'Page not found'
        # If the URI is found, but not the method, return a 405.
        elif request.method not in response_methods:
            response_headers, response_content = {'Status': 405}, 'Method not allowed'
        # Otherwise, return the headers and content from the responses.
        else:
            response_headers, response_content = response_methods[request.method]
            
        return response_headers, response_content

    def request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
        """
        The main request method. Users should override the 
        ``get_response_from_request`` method for custom response logic.
        """
        if not uri.startswith(self.root_uri):
            uri = urlparse.urljoin(self.root_uri, uri)
        
        request = self.create_request(uri, method, body, headers)

        custom_response_headers, response_content = self.get_response_from_request(request)

        # Default headers.
        response_headers = {
            'Server': 'Mock API',
            'Status': 0,
        }
        response_headers.update(custom_response_headers)

        return self.create_response(response_headers, response_content, request)

    def create_server(self, ip_address, port, handler=None):
        """
        Creates a server instance and returns it. The server instance has 
        access to this mock to provide the responses.
        """
        if handler is None:
            MockHandler.mock_api = self
            handler = MockHandler
        
        return HTTPServer((ip_address, port), handler)


class MockHandler(BaseHTTPRequestHandler):
    mock_api = None
    
    def do_GET(self):
        self.process_request('GET')
        
    def do_POST(self):
        self.process_request('POST')
        
    def do_PUT(self):
        self.process_request('PUT')
        
    def do_DELETE(self):
        self.process_request('DELETE')

    def process_request(self, method, body=None):        
        response = self.mock_api.request(self.path, method, body)

        self.send_response(response.status_code)
        for k, v in response.headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(response.raw_content)


class MockApiClient(BaseMockApiClient, ClientMixin):
    """
    A client that emulates communicating with an entire mock API.
    
    Specify each resource and some headers and/or content to return. You can
    use a ``tuple`` as response containing the headers and content, or use one
    of the available ``MockResponse`` (sub)classes to return the contents of a
    string or file.
    
    **Example**
    
    >>> client = MockApiClient(responses={
    ...     '/api/book/': {
    ...         'GET': ({'Status': 200}, [{'id': 1, 'name': 'Dive into Python', 'resource_url': 'http://localhost/api/book/1'}]),
    ...         'POST': ({'Status': 201, 'Location': 'http://localhost/api/book/2'}, ''),
    ...     },
    ...     '/api/book/1': {'GET': ({'Status': 200}, {'id': 1, 'name': 'Dive into Python', 'author': 'http://localhost/api/author/1'})},
    ...     '/api/author/': {'GET': ({'Status': 200}, [{'id': 1, 'name': 'Mark Pilgrim', 'resource_url': 'http://localhost/api/author/1'}])},
    ...     '/api/author/1': {'GET': MockResponse({'Status': 200}, {'id': 1, 'name': 'Mark Pilgrim'})}
    ... }, root_uri='http://localhost/')
    """
    pass
