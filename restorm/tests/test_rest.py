from unittest2 import TestCase

from restorm.rest import RestObject, restify


class RestObjectTests(TestCase):
    
    def test_class_functions(self):
        for func in RestObject.__dict__.keys():
            self.assertTrue(func.startswith('__'))

    def test_instance_creation(self):
        rest_object = RestObject()
        self.assertEqual(rest_object.__class__.__name__, 'DynamicRestObject')
    
    def test_empty_instance_creation(self):
        rest_object = RestObject()
        self.assertEqual(len(rest_object), 0)

    def test_instance_creation_with_data(self):
        rest_object = RestObject({'foo': 'bar'})
        self.assertEqual(len(rest_object), 1)
        
    def test_dict_behaviour(self):
        rest_object = RestObject({'foo': 'bar'})

        self.assertTrue(len(rest_object) == 1)
        self.assertTrue('foo' in rest_object)
        self.assertTrue(rest_object['foo'] == 'bar')

        rest_object['foo'] = ''
        self.assertTrue(rest_object['foo'] == '')

        del rest_object['foo']
        self.assertTrue(len(rest_object) == 0)

    def test_nested(self):
        child_object = RestObject({'foo': 'bar'})
        parent_object = RestObject({
            'child': child_object,
        })
        
        self.assertEqual(child_object.__class__.__name__, 'DynamicRestObject')
        self.assertEqual(parent_object.__class__.__name__, 'DynamicRestObject')
        
        self.assertTrue('foo' in child_object)
        self.assertFalse('foo' in parent_object)
        self.assertFalse('child' in child_object)
        self.assertTrue('child' in parent_object)


class RestifyTests(TestCase):

    def setUp(self):
        class DummyResource(object):
            client = None
        
        self.mock_resource = DummyResource()

    def test_rest_object(self):
        json_data = {
            'name': 'Dive into Python',
            'resource_url': 'http://localhost/api/book/1',
            'author': {
                'name': 'Mark Pelgrim',
                'resource_url': 'http://localhost/api/author/1',
            }
        }
        
        rest_data = restify(json_data, self.mock_resource)
        
        self.assertTrue(isinstance(rest_data, RestObject))
        #self.assertTrue(rest_data.resource_url)

        # Nested
        self.assertTrue(isinstance(rest_data['author'], RestObject))
