Mocking a REST API
==================

The mock client that comes with RestORM is an excellent method to simulate 
server side responses that you expect from a real REST API. You typically use
it in your unit tests.

There are several approaches.

Mocking predefined responses
----------------------------

You can mock a simple specific response in small tests using the 
``MockResponse`` class and subclasses, and ``MockClient``.

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


Example
~~~~~~~

An extensive example is given in the ``restorm.examples.mock`` module.

.. automodule:: restorm.examples.mock.api


Going further
-------------

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

    class MockClient(BaseMockClient, JSONClientMixin):
        pass

With the ``MockApiClient`` you can also use these mixins.
