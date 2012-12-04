Clients
=======

At the heart of RestORM you have a ``Client``. The client simply allows you to
communicate with an API and the one RestORM uses is built on top of the 
excellent `httplib2 library <http://code.google.com/p/httplib2/>`_. However, you
are free to use any HTTP client library as long as you add the RestORM mixins.

Create a client
---------------

Most RESTful API support the JSON format for their responses. A client that can
handle JSON is therefore included in RestORM.

.. autoclass:: restorm.clients.jsonclient.JSONClient

.. sourcecode:: python

    from restorm.clients.jsonclient import JSONClient
    
    client = JSONClient(root_uri='http://www.example.com/api/')
    
The ``JSONClient`` is actually a combination of the classes ``BaseClient`` and
``JSONClientMixin``. The ``BaseClient`` is responsible for communicating with 
the API while the ``JSONClientMixin`` adds serialization and deserialization for
JSON. ``JSONClient`` itself is a subclass of ``ClientMixin`` which exposes
various convenience methods.

.. autoclass:: restorm.clients.base.BaseClient
    :members: request

.. autoclass:: restorm.clients.base.ClientMixin
    :members: serialize, deserialize, create_request, create_response, get, post, put, delete

Writing your own client
-----------------------

You can tweak almost everything about the client architecture but the minimum
requirements to work with RestORM resources are:

#. You use the ``ClientMixin`` in your client.
#. Have a ``request`` function that returns a ``Response`` object.

A minimal implementation would be:

.. sourcecode:: python

    from restorm.clients.base import ClientMixin
    
    class MyClient(ClientMixin):
        def request(self, uri, method, body=None, headers=None):
            # Create request.
            request = self.create_request(uri, method, body, headers)

            # My very own client doesn't need an internet connection!
            response_headers, response_content = {'Status': 200}, 'Hello world!'
            
            # Create response.
            return self.create_response(response_headers, response_content, request)

The above client doesn't do much but it shows how to create your own client:

.. sourcecode:: python

    >>> client = MyClient()
    >>> response = client.get('/hello/')
    >>> response.content
    'Hello world!'
    >>> response.headers
    {'Status': 200}
    >>> response.request.uri
    '/hello/'

You can override any of the ``ClientMixin`` functions to add custom behaviour:

.. sourcecode:: python

    class MyClient(ClientMixin):
        # ...

        def create_request(uri, method, body=None, headers=None):
            """
            Make sure the URI is absolute.
            """
            if not uri.startswith('/'):
                uri = '/%s' % uri
            return super(MyClient, self).create_request(uri, method, body, headers)
        
        def create_response(response_headers, response_content, request):
            """
            Let everone know that it was MyClient that processed the response.
            """
            response_headers.update({
                'X-Response-Updated-By': 'MyClient'
            })
            return super(MyClient, self).create_response(response_headers, response_content, request)

.. sourcecode:: python

    >>> client = MyClient()
    >>> response = client.get('hello/')
    >>> response.content
    'Hello world!'
    >>> response.headers
    {'Status': 200, 'X-Response-Updated-By': 'MyClient'}
    >>> response.request.uri
    '/hello/'

Using different HTTP client libraries
-------------------------------------

There are lots of different client libraries. RestORM chose for ``httplib2`` as
default HTTP client library because it's an active project with built-in caching
and overall has the best performance.

Do not let the above stop you from using your own preferred HTTP client library
like `requests <http://docs.python-requests.org/en/latest/>`_,
`oauth2 <http://pypi.python.org/pypi/oauth2/>`_, or even the standard library
`httplib <http://docs.python.org/2/library/httplib.html>`_

Example: OAuth
~~~~~~~~~~~~~~

Many API's use OAuth, an open standard for authorization. It's quite simple to
incorporate the `oauth2 library <http://pypi.python.org/pypi/oauth2/>`_ in 
combination with one of the client mixins, for example the ``JSONClientMixin``
and override the ``request`` method to make a request using OAuth:

.. sourcecode:: python

    import oauth2 as oauth
    from restorm.clients.jsonclient import JSONClientMixin

    class OauthClient(oauth.Client, JSONClientMixin):
        def request(self, uri, method='GET', body=None, headers=None, *args, **kwargs):
            # Create request.
            request = self.create_request(uri, method, body, headers)

            # Perform request.
            response_headers, response_content = super(OauthClient, self).request(request.uri, request.method, request.body, request, *args, **kwargs)
            
            # Create response.
            return self.create_response(response_headers, response_content, request)

Once we have this, we can do:

.. sourcecode:: python

    >>> consumer = oauth.Consumer(key='YOUR_KEY', secret='YOUR_SECRET')
    >>> token = oauth.Token(key='YOUR_TOKEN', secret='YOUR_TOKEN_SECRET')
    >>> client = OauthClient(consumer, token)
