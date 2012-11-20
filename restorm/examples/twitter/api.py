"""
NOTE: This is *not* a complete Twitter API implementation! Its purpose is to
show you can make an implementation using RestORM.

The Twitter API v1.1 improves a lot over v1.0 by adhering to ReST-principles.
This makes the API a good example to use with RestORM.

See: https://dev.twitter.com/docs/api/1.1
"""
import urlparse
import oauth2 as oauth

from restorm.clients.jsonclient import JSONClientMixin
from restorm.resource import Resource


class TwitterClient(oauth.Client, JSONClientMixin):
    # Using the JSONClientMixin auto sets the mime type but this results in 
    # empty Twitter API responses.
    MIME_TYPE = None
    root_uri = 'https://api.twitter.com/1.1/'
    
    def request(self, uri, method='GET', body=None, headers=None, *args, **kwargs):
        # Use JSON format in this client: Set the extension to JSON.
        parsed_url = urlparse.urlparse(uri)
        if not parsed_url.path.endswith('.json'):
            uri = urlparse.urlunparse((parsed_url.scheme, parsed_url.netloc, '%s.json' % parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))

        # Create request.
        request = self.create_request(uri, method, body, headers)

        # Perform request.
        response_headers, response_content = super(TwitterClient, self).request(request.uri, request.method, request.body, request, *args, **kwargs)
        
        # Create response.
        return self.create_response(response_headers, response_content, request)


class TwitterSearch(Resource):
    class Meta:
        list = r'^search/tweets$'


class TwitterTweet(Resource):
    class Meta:
        item = r'^statuses/show?id=(?P<id>\d)$'
        list = r'^statuses/user_timeline$'