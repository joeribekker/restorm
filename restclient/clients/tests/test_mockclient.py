import os
from rest import RestObject

from unittest2 import TestCase

from restclient.clients.mockclient import MockClient, StringResponse, FileResponse, MockResponse, MockApiClient, BaseMockApiClient
from restclient.clients.jsonclient import JSONClientMixin
from restclient.resource import Resource


class MockClientTests(TestCase):
    
    def test_request_mock_response(self):
        obj = {}
        
        predefined_response = MockResponse(
            {'Foo': 'Bar', 'Status': 200},
            obj
        )
        
        client = MockClient(responses=[predefined_response,])
        url = '/some/url'
        response = client.get(url)
        
        self.assertEqual(response.content, obj)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Foo'], 'Bar')
        self.assertEqual(response.request.uri, url)

    def test_request_string_response(self):
        predefined_response = StringResponse(
            {'Foo': 'Bar', 'Status': 200},
            {}
        )
        
        client = MockClient(responses=[predefined_response,])
        url = '/some/url'
        response = client.get(url)
        
        self.assertEqual(response.content, '{}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Foo'], 'Bar')
        self.assertEqual(response.request.uri, url)

    def test_file_response_with_unknown_file(self):
        non_existent_file = '__does_not_exist__.tmp'
        self.assertFalse(os.path.isfile(non_existent_file))
        self.assertRaises(ValueError, FileResponse, {}, non_existent_file)

    def test_request_file_response(self):
        predefined_response = FileResponse(
            {'Foo': 'Bar', 'Content-Type': 'text/python', 'Status': 200},
            '%s' % __file__
        )
        
        client = MockClient(responses=[predefined_response,])
        url = '/some/url'
        response = client.get(url)
        
        self.assertTrue(self.__class__.__name__ in response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/python')
        self.assertEqual(response['Foo'], 'Bar')
        self.assertEqual(response.request.uri, url)


class MockApiClientTests(TestCase):
    def setUp(self):
        self.responses = {
            '/api/book/': {
                'GET': ({'Status': 200}, [{'id': 1, 'name': 'Dive into Python', 'resource_url': 'http://www.example.com/api/book/1'}]),
                'POST': ({'Status': 201, 'Location': 'http://www.example.com/api/book/2'}, ''),
            },
            '/api/book/1': {'GET': ({'Status': 200}, RestObject({'id': 1, 'name': 'Dive into Python', 'author': 'http://www.example.com/api/author/1'}))},
            '/api/author/': {'GET': ({'Status': 200}, [{'id': 1, 'name': 'Mark Pilgrim', 'resource_url': 'http://www.example.com/api/author/1'}])},
            '/api/author/1': {'GET': ({'Status': 200}, {'id': 1, 'name': 'Mark Pilgrim'})}
        }
        self.client = MockApiClient(responses=self.responses, root_uri='http://www.example.com')
        
    def test_get(self):
        response = self.client.get('/api/book/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, self.responses['/api/book/']['GET'][1])
        
    def test_post(self):
        response = self.client.post('/api/book/', {})
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response['Location'], self.responses['/api/book/']['POST'][0]['Location'])
        self.assertEqual(response.content, self.responses['/api/book/']['POST'][1])
        
    def test_page_not_found(self):
        uri = '/api/book/2'
        self.assertTrue(uri not in self.responses)

        response = self.client.get(uri)

        self.assertEqual(response.status_code, 404)

    def test_method_not_allowed(self):
        response = self.client.put('/api/book/1', {})

        self.assertEqual(response.status_code, 405)
        
    def test_rest_client_interaction(self):
        
        class Book(Resource):
            class Meta:
                list = r'^/api/book/$'
                item = r'^/api/book/(?P<id>\d)$'
                
        class Author(Resource):
            class Meta:
                list = r'^/api/author/$'
                item = r'^/api/author/(?P<id>\d)$'

        book = Book.objects.get(id=1, client=self.client)
        self.assertEqual(book['name'], self.responses['/api/book/1']['GET'][1]['name'])
        self.assertEqual(book['author'], self.responses['/api/book/1']['GET'][1]['author'])
        
        author = book.author
        self.assertEqual(author['name'], self.responses['/api/author/1']['GET'][1]['name'])
        

class JSONMockApiClientTests(TestCase):
    """
    Tests whether you can easily use JSONClientMixin and BaseMockApiClient to
    create a new mock client using JSON responses.
    
    This is used as an example in the README.rst
    """
    
    def setUp(self):
        self.responses = {
            '/api/book/1': {'GET': ({'Status': 200, 'Content-Type': 'application/json'}, 
                '{"id": 1, "name": "Dive into Python", "author": "http://www.example.com/api/author/1"}')}
        }

        class JSONMockApiClient(BaseMockApiClient, JSONClientMixin):
            pass

        self.client = JSONMockApiClient(responses=self.responses, root_uri='http://www.example.com')

    def test_get_json(self):
        response = self.client.get('/api/book/1')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Content-Type' in response)
        self.assertEqual(response['Content-Type'], 'application/json')

        self.assertEqual(response.content['name'], 'Dive into Python')
        self.assertEqual(response.content['author'], 'http://www.example.com/api/author/1')
