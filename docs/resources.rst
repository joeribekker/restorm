Resources
=========

REST-style architectures consist of :doc:`clients` and servers. Clients 
initiate requests to servers; servers process requests and return appropriate 
responses. Requests and responses are built around the transfer of 
representations of :doc:`resources`. A resource can be essentially any coherent
and meaningful concept that may be addressed. A representation of a resource is
typically a document that captures the current or intended state of a resource.

Let's assume we already have a client ready, as described in :doc:`clients` but
we use our mock client so you can test the demonstrated code snippets yourself.

    >>> from restorm.examples.mock.api import LibraryApiClient
    >>> client = LibraryApiClient()

Defining resources
------------------
    
Imagine a RESTful library API, like described in the :doc:`tutorial` and the
:doc:`mocking` part of this documentation. You can request a list of books in
the library and a list of authors.

.. sourcecode:: python

    from restorm.resource import Resource

    class Book(Resource):
        class Meta:
            item = r'^book/(?P<isbn>\w+)$'
            
This ``Book`` resource already allows us to get a single book from the library
API.

.. sourcecode:: python

    >>> book = Book.objects.get(isbn=1, client=client)
    >>> book.data['title']
    u'Dive into Python'

Default client
--------------
    
To make life a little easier, we can stop passing the ``client`` argument by
setting our client as the default client:

.. sourcecode:: python

    >>> from restorm.conf import settings
    >>> settings.DEFAULT_CLIENT = client

You can typically add this to your (Django) project settings so you won't have
to bother about it anymore. We can now do:

.. sourcecode:: python

    >>> book = Book.objects.get(isbn=1)
    >>> book.data['title']
    u'Dive into Python'









If we always want to get the author indirectly via a ``Book`` resource, the 
``Author`` resource we defined at the start is not even required. Why not?

At the moment, RestORM does not automatically find your resources. They