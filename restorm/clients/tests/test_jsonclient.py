import mock
from unittest2 import TestCase

from restorm.clients.jsonclient import JSONClient


@mock.patch('httplib2.Http.request')
class JSONClientTests(TestCase):
    def setUp(self):
        self.client = JSONClient()
        
    def test_get(self, request):
        request.return_value = ({'Status': 200, 'Content-Type': 'application/json'}, '{"foo": "bar"}')
        response = self.client.get(uri='http://localhost/api')
        
        data = response.content
        self.assertIsInstance(data, dict)
        self.assertTrue('foo' in data)
        self.assertEqual(data['foo'], 'bar')

    def test_incorrect_content_type(self, request):
        request.return_value = ({'Status': 200, 'Content-Type': 'foobar'}, '{"foo": "bar"}')
        response = self.client.get(uri='http://localhost/api')
        
        data = response.content
        self.assertIsInstance(data, basestring)
        self.assertEqual(data, '{"foo": "bar"}')
