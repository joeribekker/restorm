import urllib

from restclient.exceptions import RestServerException, ResourceException


class Resource(object):
    """
    Simple URL with utility methods.
    """
    def __init__(self, url, client, object_id=None):
        self.object_id = object_id
        self.client = client

        base_url = client.api_url
        
        if base_url is None:
            if not url.startswith('http'):
                raise ResourceException('Cannot resolve resource from relative URL "%s" without a base URL.' % url)

            absolute_url = url
        else:
            if not base_url.startswith('http'):
                raise ResourceException('Cannot resolve resource from relative base URL "%s".' % base_url)

            if url.startswith('http'):
                if not url.startswith(base_url):
                    raise ResourceException('Cannot resolve resource from different absolute URL "%s" as base URL "%s".' % (url, base_url))

                absolute_url = url
            else:
                if base_url.endswith('/'):
                    base_url = base_url[:-1]
                if url.startswith('/'):
                    url = url[1:]
                absolute_url = '%s/%s' % (base_url, url)
        
        if object_id is not None:
            if absolute_url.endswith('/'):
                absolute_url = '%s%s' % (absolute_url, object_id)
            else:
                absolute_url = '%s/%s' % (absolute_url, object_id)

        self.absolute_url = absolute_url
    
    def __repr__(self):
        return '<Resource: %s>' % self.absolute_url
    
    def get_object_id(self):
        if self.object_id:
            return self.object_id
        else:
            parts = self.absolute_url.split('/')
            if len(parts) > 0 and parts[-1] != '':
                return parts[-1]
            raise ResourceException('Cannot get an object ID from container resource.')

class RestManagerDescriptor(object):
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


class RestManager(object):
    
    VALID_STATUS_RESPONSES = (
        200, # OK
        304, # NOT MODIFIED
    )
    
    def __init__(self):
        self.object_class = None

    def get_or_create(self, id, data=None, client=None):
        try:
            return self.get(id, client=client), False
        except RestServerException:
            return self.create(data, client=client), True
    
    def all(self, client=None):
        return self.params(client=client)
        
    def params(self, query=None, client=None):
        c = client or default_client

        resource = Resource(self.object_class._meta.base_resource, c)

        qs = ''
        if query is not None:
            qs = '?%s' % urllib.urlencode(query)

        response = c.get('%s/%s' % (resource.absolute_url, qs))

        if response.status_code not in self.VALID_STATUS_RESPONSES:
            raise RestServerException('Cannot get "%s" (%d): %s' % (resource.absolute_url, response.status_code, response.content))
    
        # TODO: Need a lazy RestObject to fill the list... Read into Django's QuerySet.
        return response.content[self.object_class._meta.field_name]
    
    def get(self, id, client=None):
        c = client or default_client
        
        resource = Resource(self.object_class._meta.base_resource, c, id)
        response = c.get(resource.absolute_url)

        if response.status_code not in self.VALID_STATUS_RESPONSES:
            raise RestServerException('Cannot get "%s" (%d): %s' % (resource.absolute_url, response.status_code, response.content))
    
        return self.object_class(response.content, client=c, resource=resource)

    def create(self, data=None, client=None):
        if data is None:
            data = {}

        c = client or default_client

        resource = Resource(self.object_class._meta.base_resource, c)
        response = c.post('%s/' % resource.absolute_url, data=data)

        if response.status_code != 201:
            raise RestServerException('Cannot create "%s" (%d): %s' % (resource.absolute_url, response.status_code, response.content))

        # Check for path as return value. This is *NOT* a relative URL from the
        # API URL but rather the complete path without the scheme and domain.
        # Specifically, this behaviour is done by the Django test client.
        created_resource = Resource(response['Location'], c)
        # The above resource can therefore be incorrect. The object ID is fine
        # though.
        return self.get(created_resource.get_object_id(), client=c)


class RelatedResource(object):
    def __init__(self, field):
        self._field = field
    
    def _create_new_class(self, name):
        class_name = name.title().replace('_', '')
        return type(str('%sRestObject' % class_name), (RestObject,), {'__module__': '%s.auto' % RestObject.__module__})
        
    def __get__(self, instance, instance_type=None):
        if instance is None:
            return self

        if not hasattr(instance, '_cache_%s' % self._field):
            resource = Resource(instance[self._field], instance.client)
            response = instance.client.get(resource.absolute_url)
            if response.status_code == 404:
                return None
            elif response.status_code not in [200, 304]:
                raise RestServerException('Cannot get "%s" (%d): %s' % (resource.absolute_url, response.status_code, response.content))

            # NOTE: For now, use a default: RechartedObject
            #resource_class = instance.definition.get(self._field, RestObject)
            resource_class = self._create_new_class(self._field)
            setattr(instance, '_cache_%s' % self._field, resource_class(response.content, client=instance.client, resource=resource))

        return getattr(instance, '_cache_%s' % self._field, None)

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError('%s must be accessed via instance' % self._field.name)

        if isinstance(value, dict):
            resource = Resource(instance[self._field], instance.client)
            # FIXME: Ofcourse, this should not always be PUT!
            response = instance.client.put(resource.absolute_url, value)
            if response.status_code not in [200, 201, 304]:
                raise RestServerException('Cannot put "%s" (%d): %s' % (resource.absolute_url, response.status_code, response.content))

            # NOTE: For now, use a default: RechartedObject
            #resource_class = instance.definition.get(self._field, RestObject)
            resource_class = self._create_new_class(self._field)
            setattr(instance, '_cache_%s' % self._field, resource_class(value, client=instance.client, resource=resource))
        else:
            setattr(instance, '_cache_%s' % self._field, value)


class RestObjectOptions(object):
    DEFAULT_NAMES = ('base_resource', 'field_name')
    
    def __init__(self, meta):
        # Represents this RestObject's resource. For example: If the absolute URL
        # is http://localhost/api/foo/1, this is also its resource.
        self.base_resource = ''

        # Represents this RestObject's base resource. For example: If the absolute
        # URL is http://localhost/api/foo/1, the base resource would be:
        # http://localhost/api/foo (mind you, no trailing slash).
        # The base resource may also be relative to the client's API URL. For
        # example: foo
        self.field_name = ''

        # Next, apply any overridden values from 'class Meta'.
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
        
        
class RestObjectBase(type):
    """
    Meta class for RestObject. This class ensures that RestObject classes (not
    instances) are magically prepared.
    """
    
    def __new__(cls, name, bases, attrs):
        super_new = super(RestObjectBase, cls).__new__
        parents = [b for b in bases if isinstance(b, RestObjectBase)]
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
        setattr(new_class, '_meta', RestObjectOptions(meta))

        # Assign manager.
        manager = attrs.pop('objects', None)
        if manager is None:
            manager = RestManager()
        manager.object_class = new_class

        # Wrap default or custom managers such that it can only be used on
        # classes and not on instances.
        new_class.objects = RestManagerDescriptor(manager)
        
        return new_class


class RestObject(object):
    __metaclass__ = RestObjectBase

    definition = {}
    objects = None

    def __init__(self, data=None, **kwargs):
        if data is not None:
            self._obj = data
        else:
            self._obj = {}

        self._client = kwargs.pop('client', None)
        self.resource = kwargs.pop('resource', None)

        for k, v in self._obj.items():
            if isinstance(v, basestring) and v.startswith(self.client.api_url):
                # FIXME: What to do with functions and/or attributes that exist?
                if hasattr(self.__class__, k):
                    continue
                # FIXME: Hmm, runtime defined class attributes.
                setattr(self.__class__, k, RelatedResource(k))

    def __setitem__(self, key, value):
        self._obj[key] = value

    def __delitem__(self, key):
        del self._obj[key]

    def __getitem__(self, key):
        return self._obj[key]

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.resource.absolute_url)
    
    @property
    def client(self):
        return self._client or default_client