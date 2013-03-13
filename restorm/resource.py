import logging
import urllib
import re

from restorm.conf import settings
from restorm.rest import restify
from restorm.exceptions import RestServerException
from restorm.utils import reverse


VALID_GET_STATUS_RESPONSES = (
    200, # OK
    304, # NOT MODIFIED
)


class ResourceManagerDescriptor(object):
    """
    This class ensures managers aren't accessible via model instances. For
    example, Book.objects works, but book_obj.objects raises AttributeError.
    """ 
    def __init__(self, manager):
        self.manager = manager

    def __get__(self, instance, type=None):
        if instance is not None:
            raise AttributeError('Manager is not accessible via %s instances' % type.__name__)
        return self.manager


class ResourcePattern(object):
    """
    # TODO: This class needs cleaning up and refactoring.
    """

    def __init__(self, pattern, obj_path=None):
        self.pattern = pattern
        self.obj_path = obj_path

    @classmethod
    def parse(cls, obj):
        if isinstance(obj, tuple):
            return cls(*obj)
        return cls(obj)
    
    def params_from_uri(self, uri):
        return re.search(self.pattern.strip('^$'), uri).groupdict()
    
    def clean(self, response):
        if self.obj_path:
            return response.content[self.obj_path]
        return response.content 
    
    def get_url(self, query=None, **kwargs):
        if query:
            query = '?%s' % urllib.urlencode(query)
        else:
            query = ''
        return '%s%s' % (reverse(self.pattern, **kwargs), query)

    def get_absolute_url(self, root=None, query=None, **kwargs):
        if root is None:
            root = ''
        return '%s%s' % (root, self.get_url(query, **kwargs))

    
class ResourceManager(object):
    
    def __init__(self):
        self.object_class = None

    @property
    def options(self):
        try:
            return getattr(self, '_options')
        except AttributeError:
            self._options = self.object_class._meta
            return self._options

    def all(self, client=None, query=None, uri=None, **kwargs):
        """
        Returns the raw response for the list of objects. You should pass all
        arguments required by the resource URL pattern ``collection``, as
        specified in the ``Meta`` class of the resource.
        
        :param client: The client to retrieve the object from the API. By 
            default, the default client is used. If no client and no default 
            client are specified, a ``ValueError`` is raised.
        :param query: A ``dict`` with additional query string arguments. An 
            empty ``dict`` by default.
        :param uri: Rather than passing the resource URL pattern arguments, you
            can also provide a complete URL. This URL must match the resource 
            URL pattern.
        
        .. sourcecode:: python
            
            >>> Book.objects.all() # Returns a raw response.

        """
        client = client or settings.DEFAULT_CLIENT
        if client is None:
            raise ValueError('A client instance must be provided or DEFAULT_CLIENT must be set in settings.')

        rp = ResourcePattern.parse(self.options.list)
        if uri:
            kwargs = rp.params_from_uri(uri)
        absolute_url = rp.get_absolute_url(root=self.options.root, query=query, **kwargs)

        response = client.get(absolute_url)

        if response.status_code not in VALID_GET_STATUS_RESPONSES:
            raise RestServerException('Cannot get "%s" (%d): %s' % (response.request.uri, response.status_code, response.content))

        data = rp.clean(response)
        return data
    
    def get(self, client=None, query=None, uri=None, **kwargs):
        """
        Returns the object matching the given lookup parameters. You should pass
        all arguments required by the resource URL pattern ``item``, as 
        specified in the ``Meta`` class of the resource.
        
        :param client: The client to retrieve the object from the API. By 
            default, the default client is used. If no client and no default 
            client are specified, a ``ValueError`` is raised.
        :param query: A ``dict`` with additional query string arguments. An 
            empty ``dict`` by default.
        :param uri: Rather than passing the resource URL pattern arguments, you
            can also provide a complete URL. This URL must match the resource 
            URL pattern.
        
        .. sourcecode:: python
            
            >>> Book.objects.get(isbn=1)
            <Book: http://www.example.com/api/book/1>

        """
        client = client or settings.DEFAULT_CLIENT
        if client is None:
            raise ValueError('A client instance must be provided or DEFAULT_CLIENT must be set in settings.')

        rp = ResourcePattern.parse(self.options.item)
        if uri:
            kwargs = rp.params_from_uri(uri)
        absolute_url = rp.get_absolute_url(root=self.options.root, query=query, **kwargs)

        response = client.get(absolute_url)
        
        if response.status_code not in VALID_GET_STATUS_RESPONSES:
            raise RestServerException('Cannot get "%s" (%d): %s' % (response.request.uri, response.status_code, response.content))
    
        data = rp.clean(response)
        return self.object_class(data, client=client, absolute_url=response.request.uri)

    def create(self, client=None, data=None):
        """
        Roughly equivalent to a POST request, this methods creates a new entry.

        :param client: The client to retrieve the object from the API. By
            default, the default client is used. If no client and no default
            client are specified, a ``ValueError`` is raised.
        :param data: Any Python object that you want to have serialized and
            stored.
        """
        client = client or settings.DEFAULT_CLIENT
        if client is None:
            raise ValueError('A client instance must be provided or DEFAULT_CLIENT must be set in settings.')

        rp = ResourcePattern.parse(self.options.list)
        absolute_url = rp.get_absolute_url(root=self.options.root)

        response = client.post(absolute_url, data)

        # Although 201 is the best HTTP status code for a valid POST response.
        if response.status_code in [200, 201, 204]:
            if 'Location' in response:
                return self.get(client, uri=response['Location'])
            elif response.content:
                return response.content
            else:
                return None
        else:
            raise RestServerException('Cannot create "%s" (%d): %s' % (response.request.uri, response.status_code, response.content))


class RelatedResource(object):
    def __init__(self, field, resource):
        self._field = field
        self._resource = resource
        self._client = resource.client
    
    def _create_new_class(self, name):
        # FIXME: This will be a RestResource!
        class_name = name.title().replace('_', '')
        return type(str('%sResource' % class_name), (Resource,), {'__module__': '%s.auto' % Resource.__module__})
        
    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        if not hasattr(instance, '_cache_%s' % self._field):
            absolute_url = instance[self._field]
            response = self._client.get(absolute_url)
            if response.status_code == 404:
                return None
            elif response.status_code not in [200, 304]:
                raise RestServerException('Cannot get "%s" (%d): %s' % (absolute_url, response.status_code, response.content))

            resource_class = self._create_new_class(self._field)
            setattr(instance, '_cache_%s' % self._field, resource_class(response.content, client=self._client, absolute_url=absolute_url))

        return getattr(instance, '_cache_%s' % self._field, None)

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError('%s must be accessed via instance' % self._field.name)

        if isinstance(value, dict):
            absolute_url = instance[self._field]
            response = self._client.put(absolute_url, value)
            if response.status_code not in [200, 201, 304]:
                raise RestServerException('Cannot put "%s" (%d): %s' % (absolute_url, response.status_code, response.content))

            resource_class = self._create_new_class(self._field)
            setattr(instance, '_cache_%s' % self._field, resource_class(value, client=self._client, absolute_url=absolute_url))
        else:
            setattr(instance, '_cache_%s' % self._field, value)


class ResourceOptions(object):
    DEFAULT_NAMES = ('list', 'item', 'root')
    
    def __init__(self, meta):
        # Represents this Resource's list URI pattern. For example: A list of 
        # objects can be found at http://localhost/api/book/.
        self.list = ''

        # Represents this Resource's item URI pattern. For example: A single
        # object of this resource can be found at http://localhost/api/book/1.
        self.item = ''

        # Indicates the root of the resource. In some cases, a resource is
        # found on a different domain or service. For example: If the regular
        # resource can be found on http://localhost/api/ the search engine
        # might be found on http://search.localhost/api/. If so, set root to
        # this different URL.
        self.root = ''

        # Next, apply any overridden values from 'class Meta'.
        # TODO: This might be a good place to store ResourcePatterns.
        if meta:
            meta_attrs = meta.__dict__.copy()
            for name in meta.__dict__:
                # Ignore any private attributes that Django doesn't care about.
                # NOTE: We can't modify a dictionary's contents while looping
                # over it, so we loop over the *original* dictionary instead.
                if name.startswith('_'):
                    del meta_attrs[name]
            for attr_name in self.DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))
                elif hasattr(meta, attr_name):
                    setattr(self, attr_name, getattr(meta, attr_name))
        
        
class ResourceBase(type):
    """
    Meta class for Resource. This class ensures that Resource classes (not
    instances) are magically prepared.
    """
    
    def __new__(cls, name, bases, attrs):
        super_new = super(ResourceBase, cls).__new__
        parents = [b for b in bases if isinstance(b, ResourceBase)]
        if not parents:
            # If this isn't a subclass of RestObject, don't do anything 
            # special.
            return super_new(cls, name, bases, attrs)

        # Create the class and strip all its attributes, except the module.
#        module = attrs.pop('__module__')
#        new_class = super_new(cls, name, bases, {'__module__': module})
        new_class = super_new(cls, name, bases, attrs)
        
        # Create the meta class.
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        base_meta = getattr(new_class, '_meta', None)
        setattr(new_class, '_meta', ResourceOptions(meta))

        # Assign manager.
        manager = attrs.pop('objects', None)
        if manager is None:
            manager = ResourceManager()
        manager.object_class = new_class

        # Wrap default or custom managers such that it can only be used on
        # classes and not on instances.
        new_class.objects = ResourceManagerDescriptor(manager)
        
        return new_class


class ResourceList(list):
    """
    A list of ``Resource`` instances which are most likely incomplete compared
    to when they are retrieved as an individual.
    """
    def __init__(self, data, **kwargs):
        self.client = kwargs.pop('client', None)
        self.absolute_url = kwargs.pop('absolute_url', None)
        
        super(ResourceList, self).__init__([Resource(item, self.client) for item in data])


class Resource(object):
    """
    Class that holds information about a resource.

    It has a manager to retrieve and/or manipulate the state of a resource.
    """
    __metaclass__ = ResourceBase

    objects = None

    def __init__(self, data=None, client=None, absolute_url=None):
        self.client = client
        self.absolute_url = absolute_url

        self.data = restify(data, self)

    def __unicode__(self):
        return self.absolute_url
    
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.__unicode__())

    def save(self):
        """
        Performs a PUT request to update the object.

        No guarantees are given to what this method actually returns due to the
        freedom of API implementations. If there is a body in the response, the
        contents of this body is returned, otherwise ``None``.
        """

        response = self.client.put(self.absolute_url, self.data)

        # Although 204 is the best HTTP status code for a valid PUT response.
        if response.status_code in [200, 201, 204]:
            if response.content:
                return response.content
            else:
                return None
        else:
            raise RestServerException('Cannot create "%s" (%d): %s' % (response.request.uri, response.status_code, response.content))


class SimpleResource(object):
    """
    Class that holds information about a resource.
    
    It has a manager to retrieve and/or manipulate the state of a resource. 
    """
    __metaclass__ = ResourceBase

    objects = None

    def __init__(self, data=None, client=None, absolute_url=None):
        self.client = client
        self.absolute_url = absolute_url
        
        self.data = data

    def __unicode__(self):
        return self.absolute_url
    
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.__unicode__())

    def save(self):
        self.client.put(self.absolute_url, self.data)