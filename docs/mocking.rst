Mocking
=======

The mock client that comes with RestORM is an excellent method to simulate 
server side responses that you expect from a real REST API. You typically use
it in your unit tests.

You can switch out your client with a mock client and simply work as usual, 
given that you mocked some typical responses. The mocking works transparently
with ``Resource`` classes. Just pass your mock client to it.

Where you would normally have::

    >>> from restorm.resource import Resource
    >>> class Book(Resource):
    ...     class Meta:
    ...         item = r'^book/(?P<isbn>\w+)$'

    >>> from restorm.clients.jsonclient import JSONClient
    >>> client = JSONClient(root_uri='http://www.example.com/api/')

    >>> book = Book.objects.get(isbn='978-1441413024', client=client)
    >>> book.data['title']
    u'Dive into Python'

You can replace it all with mocking behaviour that does not rely on actual
communication with the external API::

    >>> from restorm.clients.mockclient import MockApiClient
    >>> mock_client = MockApiClient(
    ...     root_uri='http://www.example.com/api/',
    ...     responses={
    ...         'book/978-1441413024': {
    ...             'GET': ({'Status': 200}, {'title': 'Dive into Python'})
    ...         }
    ...     }
    ... )

    >>> book = Book.objects.get(isbn='978-1441413024', client=mock_client)
    >>> book.data['title']
    u'Dive into Python'

There are several approaches.

Mocking single predefined responses
-----------------------------------

You can mock a simple specific response in small tests using the 
``MockResponse`` class and subclasses, and ``MockClient``. You typically use
these classes where you do not want to mock an entire API and can suffice with
just a few responses that don't happen irregularly.

.. autoclass:: restorm.clients.mockclient.MockResponse

.. autoclass:: restorm.clients.mockclient.StringResponse

.. autoclass:: restorm.clients.mockclient.FileResponse

Using the above classes, you can pass desired responses to your mock client.

.. autoclass:: restorm.clients.mockclient.MockClient

Mocking entire servers
----------------------

If you are going to test alot against a certain API (your own, or an external 
one), it might be a good idea to make mock the a part of the API. You typically
use this to make functional tests or broader unit tests. You can use the 
``MockApiClient`` for this purpose.

You can even create a web server from a ``MockApiClient`` instance to "browse"
through your mock API using a browser or keep it running to let your 
application talk to it.

.. autoclass:: restorm.clients.mockclient.MockApiClient
    :members: get_response_from_request, create_server

Example: Library API
~~~~~~~~~~~~~~~~~~~~

An extensive example is given in the ``restorm.examples.mock`` module that 
extends the mock API from the :doc:`tutorial`.

.. automodule:: restorm.examples.mock.api


Expanding on what's there
-------------------------

Both the ``MockClient`` and ``MockApiClient`` constist of a base class and a 
mixin that handles the specifics. The ``MockClient`` class is defined as:

.. sourcecode:: python
    
    from restorm.clients.base import ClientMixin
    from restorm.clients.mockclient import BaseMockClient
    
    class MockClient(BaseMockClient, ClientMixin):
        pass

You can easily use these classes for your own use. Actually, creating a mock
client that serves JSON is nothing more than:

.. sourcecode:: python

    from restorm.clients.jsonclient import JSONClientMixin

    class MockJSONClient(BaseMockClient, JSONClientMixin):
        pass

With the ``MockApiClient`` you can also use these mixins:

.. sourcecode:: python

    from restorm.clients.jsonclient import JSONClientMixin, json
    from restorm.clients.mockclient import BaseMockApiClient

    class MockApiJSONClient(BaseMockApiClient, JSONClientMixin):
        pass

