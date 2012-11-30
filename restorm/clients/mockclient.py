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
    
    >>> from restorm.clients.mockclient import MockResponse
    >>> response = MockResponse({'Status': 200}, {'foo': 'bar'})
    >>> response.headers
    {'Status': 200}
    >>> response.content
    {'foo': 'bar'}

    """
    def __init__(self, headers, content):
        self.headers = headers
        self.content = content

        super(MockResponse, self).__init__((headers, content))


class StringResponse(MockResponse):
    """
    A response with stringified content.
    
    >>> from restorm.clients.mockclient import StringResponse
    >>> response = StringResponse({'Status': 200}, '{}')
    >>> response.content
    '{}'

    """
    def __init__(self, headers, content):
        super(StringResponse, self).__init__(headers, unicode(content))


class FileResponse(MockResponse):
    """
    A response with the contents of a file, read by absolute file path.

    >>> from restorm.clients.mockclient import FileResponse
    >>> response = FileResponse({'Status': 200}, 'response.json')

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
            raise ValueError('Ran out of responses when requesting: %s' % uri)

        if not uri.startswith(self.root_uri):
            urlparse.urljoin(self.root_uri, uri)

        request = self.create_request(uri, method, body, headers)

        # Get current queued mock response.
        response = self.responses[self._response_index]
        self._response_index += 1

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
    responses. You can add any ``MockResponse`` sub class to the ``responses``
    argument.
    
    It doesn't matter what URI you request or what data you pass in the body,
    the first response you added is just returned on the first request.
    
    Responses are popped from a queue. This means that if you add 3 responses,
    you can only make 3 requests before a ``ValueError`` is raised.
    
    >>> from restorm.clients.mockclient import MockClient, StringResponse
    >>> desired_response = StringResponse({'Status': 200}, '{}')
    >>> mock_client = MockClient('http://mockserver/', responses=[desired_response,])
    >>> response = mock_client.get('/') # Can be any URI.
    >>> response.content
    u'{}'
    >>> response.status_code
    200
    >>> response = mock_client.get('/') # Another call.
    ValueError: Ran out of responses when requesting: /

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
        this container variable or even mutate the ``responses`` variable based
        on the request.
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
        
        >>> from restorm.clients.mockclient import MockApiClient, StringResponse
        >>> mock_api_client = MockApiClient(responses={'/': {'GET': ({'Status': 200}, 'My homepage')}})
        >>> server = mock_api_client.create_server('127.0.0.1', 8000)
        >>> server.serve_forever()

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
    
    The structure of the ``responses`` is::
    
        {<relative URI>: {<HTTP method>: ({<header key>: <header value>, ...}, <response content>)}}
    
    >>> from restorm.clients.mockclient import MockApiClient, StringResponse
    >>> mock_api_client = MockApiClient(responses={
    ...     'book/': {
    ...         'GET': ({'Status': 200}, [{'id': 1, 'name': 'Dive into Python', 'resource_url': 'http://localhost/api/book/1'}]),
    ...         'POST': ({'Status': 201, 'Location': 'http://localhost/api/book/2'}, ''),
    ...     },
    ...     'book/1': {'GET': ({'Status': 200}, {'id': 1, 'name': 'Dive into Python', 'author': 'http://localhost/api/author/1'})},
    ...     'author/': {'GET': ({'Status': 200}, [{'id': 1, 'name': 'Mark Pilgrim', 'resource_url': 'http://localhost/api/author/1'}])},
    ...     'author/1': {'GET': FileResponse({'Status': 200}, 'response.json')}
    ... }, root_uri='http://localhost/api/')
    ...
    >>> response = mock_api_client.get('http://localhost/api/book/1')
    >>> response.content
    {'id': 1, 'name': 'Dive into Python', 'author': 'http://localhost/api/author/1'}
    >>> response.status_code
    200

    """
    pass
