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
        
        self.assertIsInstance(rest_data, RestObject)
        #self.assertTrue(rest_data.resource_url)

        # Nested
        self.assertIsInstance(rest_data['author'], RestObject)

#    def test(self):
#        # Before anything is instantiated, Book and RestObject should not have
#        # attributes referring to related objects.
#        self.assertFalse(hasattr(Book, 'author'))
#        self.assertFalse(hasattr(Resource, 'author'))
#
#        book = Book.objects.get(client=self.client, id=1)
#
#        # The book has a registered class, Book.
#        self.assertTrue(isinstance(book, Book))
#        self.assertTrue(isinstance(book, Resource))
#
#        # The Book class should have an author attribute after instantation...
#        self.assertTrue(hasattr(Book, 'author'))
#        # ... the RestObject (base) class should not.
#        self.assertFalse(hasattr(RestObject, 'author'))
#
#        # Test basic book resource properties.
#        self.assertEqual(book.absolute_url, 'http://localhost/api/book/1')
#        self.assertEqual(book['title'], book_data['title'])
#        self.assertEqual(book['author'], book_data['author'])
#
#        # The author attribute should be present on the instance, bot not yet
#        # cached.
#        self.assertFalse(hasattr(book, '_cache_author'), 'Author should lazely be retrieved.')
#        self.assertTrue(hasattr(book, 'author'))
#
#        author = book.author
#
#        # The author does not have a registered class, thus is a
#        # Author-RestObject.
#        self.assertTrue(isinstance(author, RestObject))
#
#        # After retrieving the author, the author should be cached on the
#        # instance, not on the class.
#        self.assertTrue(hasattr(book, '_cache_author'))
#        self.assertFalse(hasattr(Book, '_cache_author'))
#
#        # The RestObject class should still not have an attribute called author
#        # and neither should the author instance.
#        self.assertFalse(hasattr(RestObject, 'author'))
#        self.assertFalse(hasattr(author, 'author'))
#
#        # Test basic author resource properties.
#        self.assertEqual(author.absolute_url, 'http://localhost/api/author/1')
#        self.assertEqual(author['name'], author_data['name'])
#
#        city = author.born_in
#
#        # The city does not have a registered class, thus is a City-RestObject.
#        self.assertTrue(isinstance(city, RestObject))
#
#        # Here we check if the auto created class CityRestObject does not have
#        # attributes that belong to AuthorRestObject.
#        self.assertFalse(hasattr(RestObject, 'born_in'))
#        self.assertFalse(hasattr(city, 'born_in'))
#
#        self.assertFalse(hasattr(RestObject, 'author'))
#        self.assertFalse(hasattr(city, 'author'))
#        self.assertFalse(hasattr(book, 'born_in'))
#
#        self.assertTrue(hasattr(author, '_cache_born_in'))
#        self.assertFalse(hasattr(city, '_cache_born_in'))
#        self.assertFalse(hasattr(book, '_cache_born_in'))
#
#        # Test basic city resource properties.
#        self.assertEqual(city.absolute_url, 'http://localhost/api/city/1')
#        self.assertEqual(city['name'], city_data['name'])
