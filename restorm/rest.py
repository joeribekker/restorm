from restorm.clients.jsonclient import json


class RestObject(object):
    """
    A ``dict``-like object without the convenience methods.
    """
    def __new__(cls, data=None, *args, **kwargs):
        from resource import RelatedResource

        resource = kwargs.get('resource')
        related_resources = {}
        if data is not None:
            for k, v in data.items():
                # FIXME: Checking for http only is a bit crude.
                if isinstance(v, basestring) and v.startswith('http'):
                    if not hasattr(cls, k):
                        related_resources[k] = RelatedResource(k, resource)

        new_class = type('Dynamic%s' % cls.__name__, (cls,), related_resources)
        return super(RestObject, cls).__new__(new_class)
    
    def __init__(self, data=None, **kwargs):
        
        if data is not None:
            self._obj = data
        else:
            self._obj = {}

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self._obj.__repr__())

    # Interface: collections.MutableMapping
    def __getitem__(self, key):
        return self._obj[key]

    def __setitem__(self, key, value):
        self._obj[key] = value

    def __delitem__(self, key):
        del self._obj[key]

    def __len__(self):
        return len(self._obj)

    def __iter__(self):
        return self._obj.__iter__()


def restify(data, resource):
    """
    Turns Python objects (dict, list, etc) into Rest objects.
    
    :param data: Any Python object.
    :param resource: The resource this data belongs to.

    :return: Rest objects. 
    """
    def rest_object(dct):
        return RestObject(dct, resource=resource)
    
    json_data = json.dumps(data)
    return json.loads(json_data, object_hook=rest_object)
