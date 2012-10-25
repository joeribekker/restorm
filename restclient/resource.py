import logging
import urllib

from restclient.rest import RestObject
from restclient.exceptions import RestServerException
from restclient.utils import reverse


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

    def __init__(self, pattern, obj_path=None):
        self.pattern = pattern
        self.obj_path = obj_path

    @classmethod
    def parse(cls, obj):
        if isinstance(obj, tuple):
            return cls(*obj)
        return cls(obj)

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
    
    VALID_STATUS_RESPONSES = (
        200, # OK
        304, # NOT MODIFIED
    )
    
    def __init__(self):
        self.object_class = None

    def all(self, client=None, query=None, **kwargs):
        opts = self.object_class._meta
        # FIXME: This can be done once and retrieved every time...
        rd = ResourcePattern.parse(opts.list)
        absolute_url = rd.get_absolute_url(root=opts.root, query=query, **kwargs)

        response = client.get(absolute_url)

        if response.status_code not in self.VALID_STATUS_RESPONSES:
            raise RestServerException('Cannot get "%s" (%d): %s' % (response.request.uri, response.status_code, response.content))
        
        return rd.clean(response)
    
    def get(self, client=None, query=None, **kwargs):
        opts = self.object_class._meta
        # FIXME: This can be done once and retrieved every time...
        rd = ResourcePattern.parse(opts.item)
        absolute_url = rd.get_absolute_url(root=opts.root, query=query, **kwargs)

        response = client.get(absolute_url)
        
        if response.status_code not in self.VALID_STATUS_RESPONSES:
            raise RestServerException('Cannot get "%s" (%d): %s' % (response.request.uri, response.status_code, response.content))
    
        return self.object_class(response.content, client=client, absolute_url=response.request.uri)


class RelatedResource(object):
    def __init__(self, field):
        self._field = field
    
    def _create_new_class(self, name):
        # FIXME: This will be a RestResource!
        class_name = name.title().replace('_', '')
        return type(str('%sResource' % class_name), (Resource,), {'__module__': '%s.auto' % Resource.__module__})
        
    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        if not hasattr(instance, '_cache_%s' % self._field):
            absolute_url = instance[self._field]
            response = instance.client.get(absolute_url)
            if response.status_code == 404:
                return None
            elif response.status_code not in [200, 304]:
                raise RestServerException('Cannot get "%s" (%d): %s' % (absolute_url, response.status_code, response.content))

            resource_class = self._create_new_class(self._field)
            setattr(instance, '_cache_%s' % self._field, resource_class(response.content, client=instance.client, absolute_url=absolute_url))

        return getattr(instance, '_cache_%s' % self._field, None)

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError('%s must be accessed via instance' % self._field.name)

        if isinstance(value, dict):
            absolute_url = instance[self._field]
            response = instance.client.put(absolute_url, value)
            if response.status_code not in [200, 201, 304]:
                raise RestServerException('Cannot put "%s" (%d): %s' % (absolute_url, response.status_code, response.content))

            resource_class = self._create_new_class(self._field)
            setattr(instance, '_cache_%s' % self._field, resource_class(value, client=instance.client, absolute_url=absolute_url))
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


class Resource(object):
    """
    Class that holds information about a resource.
    
    It has a manager to retrieve and/or manipulate the state of a resource. 
    """
    __metaclass__ = ResourceBase

    objects = None

    def __init__(self, data=None, **kwargs):
        self.client = kwargs.pop('client', None)
        self.absolute_url = kwargs.pop('absolute_url', None)
        
        self._data = data

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.absolute_url)

    # TODO: Allow this resource to act as a list, dict, or whatever.
    # Interface: collections.MutableMapping
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return self._data.__iter__()
