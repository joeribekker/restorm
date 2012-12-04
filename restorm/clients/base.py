import logging
import urlparse
import httplib2


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
        self.raw_content = response_content
        self.content = response_content
        self.request = request

        # Make headers consistently accessible. 
        self.update(dict([(k.title().replace('_', '-'), v) for k, v in response_headers.items()]))
        
        # Set status code on its own property.
        self.status_code = int(self.pop('Status'))


class ClientMixin(object):
    """
    This mixin contains the attribute ``MIME_TYPE`` which is ``None`` by
    default. Subclasses can set it to some mime-type that will be used as 
    ``Content-Type`` and ``Accept`` header in requests.
    
    If the ``MIME_TYPE`` is also found in the ``Content-Type`` response headers,
    the response contents will be deserialized.
    """
    root_uri = ''

    MIME_TYPE = None
    
    def serialize(self, data):
        """
        Produces a serialized version suitable for transfer over the wire.
        
        Subclasses should override this function to implement their own 
        serializing scheme. This implementation simply returns the data passed
        to this function.

        Data from the serialize function passed to the deserialize function, 
        and vice versa, should return the same value.
        
        :param data: Data.
        
        :return: Serialized data.
        """
        return data
    
    def deserialize(self, data):
        """
        Deserialize the data from the raw data.
        
        Subclasses should override this function to implement their own 
        deserializing scheme. This implementation simply returns the data
        passed to this function.

        Data from the serialize function passed to the deserialize function, 
        and vice versa, should return the same value.
        
        :param data: Serialized data.
        
        :return: Data.
        """
        return data
    
    def create_request(self, uri, method, body=None, headers=None):
        """
        Returns a ``Request`` object.
        """
        if not uri.startswith(self.root_uri):
            uri = urlparse.urljoin(self.root_uri, uri)

        if headers is None:
            headers = {}

        if self.MIME_TYPE:
            headers.update({
                'Accept': self.MIME_TYPE,
                'Content-Type': self.MIME_TYPE,
            })

        data = self.serialize(body)

        return Request(uri, method, data, headers)
    
    def create_response(self, response_headers, response_content, request):
        """
        Returns a ``Response`` object.
        """
        response = Response(self, response_headers, response_content, request)

        if not self.MIME_TYPE or ('Content-Type' in response and response['Content-Type'].startswith(self.MIME_TYPE)):
            response.content = self.deserialize(response_content)

        return response 

    def get(self, uri):
        """
        Convenience method that performs a GET-request.
        """
        return self.request(uri, 'GET')

    def post(self, uri, data):
        """
        Convenience method that performs a POST-request.
        """
        return self.request(uri, 'POST', data)

    def put(self, uri, data):
        """
        Convenience method that performs a PUT-request.
        """
        return self.request(uri, 'PUT', data)

    def delete(self, uri):
        """
        Convenience method that performs a DELETE-request.
        """
        return self.request(uri, 'DELETE')


class BaseClient(httplib2.Http):
    """
    Simple RESTful client based on ``httplib2.Http``.
    """
    def __init__(self, *args, **kwargs):
        """
        Takes one additional argument ``root_uri``. All other arguments are 
        passed to the ``httplib2.Http`` constructor.
        """
        if 'root_uri' in kwargs:
            self.root_uri = kwargs.pop('root_uri')

        super(BaseClient, self).__init__(*args, **kwargs)
    
    def request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
        """
        Creates a ``Request`` object by calling 
        ``self.create_request(uri, method, body, headers)`` and performs the low
        level HTTP-request using this request object. A ``Response`` object is
        created with the data returned from the request, by calling
        ``self.create_response(response_headers, response_content, request)``
        and is returned.
        """
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