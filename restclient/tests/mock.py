import os

from restclient.base import Client, Response


class MockResponse(object):
    """
    Base class for mocked responses. Headers can be provided as dict. The 
    content is simply returned as response and is usually a string.
    """
    def __init__(self, headers, content):
        self.headers = headers
        self.content = content


class StringResponse(MockResponse):
    """
    A response comming from a string.

    **Example**

    >>> desired_response = StringResponse({'Status': 200}, '{}')
    """
    pass


class FileResponse(MockResponse):
    """
    A response comming from an absolute file path.

    **Example**
    
    >>> desired_response = StringResponse({'Status': 200}, 'response.json')
    """
    def __init__(self, headers, filepath):
        if not os.path.isfile(filepath):
            raise ValueError('Cannot find file "%s".' % filepath)

        f = open(filepath)
        content = f.read()
        f.close()
        
        super(FileResponse, self).__init__(headers, content)


class SimpleMockClient(Client):
    """
    A mock client, emulating the rest client. The client returns predefined 
    responses.
    
    You can add fake response as either a StringResponse or a FileResponse. The
    first argument of these classes should always be a dict of headers, the 
    second argument is the content as string or file path respectively.
    
    **Example**

    >>> desired_response = StringResponse({'Status': 200}, '{}')
    >>> client = SimpleMockClient('http://mockserver/', responses=[desired_response,])
    >>> response = client.get('/')
    >>> response.content
    {}
    >>> response.status_code
    200
    """
    responses = []
    
    def __init__(self, *args, **kwargs):
        self.responses = kwargs.pop('responses', [])
        self._counter = 0
        
        super(SimpleMockClient, self).__init__(*args, **kwargs)
        
    def request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
        if self._counter >= len(self.responses):
            raise RuntimeError('Ran out of responses when requesting: %s' % uri )
        
        if not uri.startswith('http'):
            uri = '%s%s' % (self.api_url, uri)

        request_headers = {
            'Content-Type': 'application/json',
            'X-API-version': '1',
            'Authorization': self._authorization
        }
        if headers:
            request_headers.update(headers)

        request = {
            'PATH_INFO': uri,
            'REQUEST_METHOD': method,
            'QUERY_STRING': '',
        }
        request.update(dict([(k.upper().replace('-', '_'), v) for k, v in request_headers.items()]))
        
        response_headers = {
            'Server': 'Mock Client',
            'Status': 0,
            'Content-Type': request_headers['Content-Type']
        }
        response_headers.update(self.responses[self._counter].headers)
        response_content = self.responses[self._counter].content
        
        self._counter += 1
        
        return Response(self, (response_headers, response_content), request)    