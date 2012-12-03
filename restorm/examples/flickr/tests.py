from unittest2 import TestCase, skipIf

from restorm.examples.flickr import api

try:
    from settings_local import FLICKR_SETTINGS
except ImportError:
    FLICKR_SETTINGS = None


class FlickrLiveTests(TestCase):
    
    def setUp(self):
        self.client = api.FlickrClient(FLICKR_SETTINGS['API_KEY'])
    
    @skipIf(FLICKR_SETTINGS is None, 'You must provide "FLICKR_SETTINGS" in your "settings_local.py". See: "settings_local_example.py".')
    def test_get_recent(self):
        recent_photos = api.FlickrPhoto.objects.get_recent(client=self.client)
        self.assertTrue(len(recent_photos) > 0, 'No search results for recent photo\'s? This cannot be correct!')
        
        photo = recent_photos[0]
        
        self.assertTrue('title' in photo.data)
        self.assertFalse('description' in photo.data)
        self.assertTrue(photo.get_url().endswith('.jpg'))

    @skipIf(FLICKR_SETTINGS is None, 'You must provide "FLICKR_SETTINGS" in your "settings_local.py". See: "settings_local_example.py".')
    def test_get(self):
        recent_photos = api.FlickrPhoto.objects.get_recent(client=self.client)
        self.assertTrue(len(recent_photos) > 0, 'No search results for recent photo\'s? This cannot be correct!')
        
        # Retrieve details of this photo.
        photo = api.FlickrPhoto.objects.get(id=recent_photos[0].data['id'], client=self.client)
        self.assertTrue('title' in photo.data)
        self.assertTrue('description' in photo.data)
        self.assertTrue(photo.get_url().endswith('.jpg'))