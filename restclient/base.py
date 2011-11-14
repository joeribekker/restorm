import httplib2
import base64

try:
    import json
except ImportError:
    # Python 2.5 compatability.
    import simplejson as json


class Response(dict):
    def __init__(self, client, response, request):
        super(Response, self).__init__()
        self.client = client
        self.request = request
        self.update(dict([(k.title(), v) for k, v in response[0].items()]))
        self.status_code = int(self.pop('Status'))

        if self['Content-Type'].startswith('application/json'):
            self.content = json.loads(response[1])
        else:
            self.content = response[1]

            
class Client(httplib2.Http):
    """
    Simple REST client based on ``httplib2.Http``.
    
    This client behaves similar to the one provided by Django's testsuite.
    """
    def __init__(self, api_url=None, username=None, password=None):
        super(Client, self).__init__('.cache', disable_ssl_certificate_validation=True)
        self.api_url = api_url
        self._authorization = 'Basic %s' % base64.encodestring('%s:%s' % (username, password))

    def request(self, uri, method='GET', body=None, headers=None, redirections=5, connection_type=None):
        if not uri.startswith('http'):
            uri = '%s%s' % (self.api_url, uri)

        request_headers = {
            'Content-Type': 'application/json',
            'X-API-version': '1',
            'Authorization': self._authorization
        }
        if headers:
            request_headers.update(headers)

        response = super(Client, self).request(uri, method, body, request_headers, redirections, connection_type)
        
        request = {
            'PATH_INFO': uri,
            'REQUEST_METHOD': method,
            'QUERY_STRING': '',
        }
        request.update(dict([(k.upper().replace('-', '_'), v) for k, v in request_headers.items()]))
        
        return Response(self, response, request)

    def get(self, uri, data=None):
        if data is None:
            data = {}
        return self.request(uri, 'GET', data)

    def post(self, uri, data):
        return self.request(uri, 'POST', json.dumps(data))

    def put(self, uri, data):
        return self.request(uri, 'PUT', json.dumps(data))

    def delete(self, uri):
        return self.request(uri, 'DELETE')
