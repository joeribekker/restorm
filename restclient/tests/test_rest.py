from unittest2 import TestCase

from restclient.rest import RestObject


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

    def test_related(self):
        rest_object = RestObject({'foo': 'bar', 'resource': 'http://www.example.com/api/object'})
        
        self.assertEqual(rest_object['foo'], 'bar')
        self.assertEqual(rest_object['resource'], 'http://www.example.com/api/object')
        
        self.assertFalse(hasattr(rest_object, 'foo'))
        self.assertFalse(hasattr(rest_object, 'resource'))

        self.assertFalse(hasattr(rest_object.__class__, 'foo'))
        self.assertTrue(hasattr(rest_object.__class__, 'resource'))

    def test_nested_related(self):
        child_object = RestObject({'foo': 'bar', 'child_resource': 'http://www.example.com/api/child_object'})
        parent_object = RestObject({
            'child': child_object,
            'parent_resource': 'http://www.example.com/api/parent_object'
        })
        
        # TODO