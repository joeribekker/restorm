"""
NOTE: This is *not* a complete Flickr API implementation! Its purpose is to
show you can make an implementation using RestORM.

The Flickr API can be accessed as a ReST webservice. Although it's very limited
and not really a good example of ReST, it's a popular service.

With Flickr, you can actually make a single ``Resource`` that can address all 
functions of Flickr using the query argument. Well, that would defeat the whole
purpose of RestORM.

See: http://www.flickr.com/services/api/
"""
import urllib
import urlparse

from restorm.clients.base import BaseClient
from restorm.clients.jsonclient import JSONClientMixin
from restorm.resource import Resource, ResourceManager


class FlickrPhotoManager(ResourceManager):
    def get_recent(self, client, extras=None, per_page=None, page=None):
        """
        Get recent public photo's from Flickr.
        
        See: http://www.flickr.com/services/api/flickr.photos.getRecent.html
        """
        result = self.all(client, query={'method': 'flickr.photos.getRecent'})

        # Create a list of individual FlickrPhoto instances from the response.
        photos = []
        for index, element in enumerate(result['photos']['photo']):
            photos.append(
                FlickrPhoto(data=element, client=client)
            )
            
        return photos
        
        
class FlickrPhoto(Resource):
    PHOTO_URL = u'http://farm%(farm_id)d.staticflickr.com/%(server_id)s/%(id)s_%(secret)s.jpg'
    
    objects = FlickrPhotoManager()
    
    class Meta:
        # You could instead create a get_info function on the 
        # ``FlickrPhotoManager`` but this shows you can also use it as if this
        # method is to retrieve a single photo. The default ``get`` behaviour
        # on the manager does all the work for you in this case.
        item = (r'^?method=flickr.photos.getInfo&&photo_id=(?P<id>\d)$', 'photo')

    def get_url(self):
        """
        Return the constructed URL to the photo from the data.
        
        See: http://www.flickr.com/services/api/misc.urls.html
        """
        return self.PHOTO_URL % {
            'farm_id': self.data['farm'],
            'server_id': self.data['server'],
            'id': self.data['id'],
            'secret': self.data['secret'],
        }


class FlickrClient(BaseClient, JSONClientMixin):
    root_uri = 'http://api.flickr.com/services/rest/'
    
    def __init__(self, api_key, *args, **kwargs):
        self.api_key = api_key
        super(FlickrClient, self).__init__(*args, **kwargs)

    def request(self, uri, method='GET', body=None, headers=None, *args, **kwargs):
        if body is None:
            body = ''
            
        # Add query paramaters that always need to be present for this client.
        default_query_params = {
            'api_key': self.api_key,
            'format': 'json',
            'nojsoncallback': '1',
        }

        # Update uri with default query params.        
        url_parts = list(urlparse.urlparse(uri))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(default_query_params)
        url_parts[4] = urllib.urlencode(query)
        
        uri = urlparse.urlunparse(url_parts)

        return super(FlickrClient, self).request(uri, method, body, headers, *args, **kwargs)
