import logging
import httplib2

try:
    import json
except ImportError:
    # Python 2.5 compatability.
    import simplejson as json


logger = logging.getLogger(__name__)


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
        try:
            response_headers, response_content = super(BaseClient, self).request(request.uri, request.method, request.body, request, redirections, connection_type)
        except Exception, e:
            # Logging.
            logger.critical('%(method)s %(uri)s\n%(headers)s\n\n%(body)s\n\n\nException: %(exception)s', {
                'method': request.method,
                'uri': request.uri,
                'headers': '\n'.join(['%s: %s' % (k, v) for k, v in request.items()]),
                'body': request.body if request.body else '',
                'exception': unicode(e),
            })
            raise
        else:
            # Create response.
            response = self.create_response(response_headers, response_content, request)
            
            # Logging.
            if logger.level > logging.DEBUG:
                logger.info('%(method)s %(uri)s (HTTP %(response_status)s)' % {
                    'method': request.method,
                    'uri': request.uri,
                    'response_status': response.status_code
                })
            else:
                logger.debug('%(method)s %(uri)s\n%(headers)s\n\n%(body)s\n\n\nHTTP %(response_status)s\n%(response_headers)s\n\n%(response_content)s', {
                    'method': request.method,
                    'uri': request.uri,
                    'headers': '\n'.join(['%s: %s' % (k, v) for k, v in request.items()]),
                    'body': request.body if request.body else '',
                    'response_status': response.status_code,
                    'response_headers': '\n'.join(['%s: %s' % (k, v) for k, v in response.items()]),
                    # Show the actual content, not response.content
                    'response_content': response_content
                })
                
            return response


class Client(BaseClient, ClientMixin):
    pass