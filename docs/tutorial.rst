Tutorial
========

In this tutorial we'll walk you through the creation of a simple client-side
implementation of a RESTful library API. This shows you the basics of RestORM.
This example is included in the source code of RestORM and has more features,
see: ``restorm.examples.mock``.

Let's examine the server-side of the library API. Normally you would read the
documentation of a RESTful API since there is no standard (yet) to describe a 
RESTful API and have a computer generate a proxy.

The library API
---------------

Below, you'll find an example of how the library API could be documented. The
library contains books and each book is ofcourse written by an author. For the 
sake of this tutorial, it doesn't expose a lot of features:

Welcome to the documentation for our library API! All resources are available on
``http://www.example.com/api/``. No authentication is required and responses are
in JSON format.

* **GET** ``book/`` -- Returns a list of available books in the library::
    
        [
            {
                "isbn": 1,
                "title": "Dive into Python", 
                "resource_url": "http://www.example.com/api/book/1"
            },
            # ...
        ]

* **GET** ``book/{id}`` -- Returns a specific book, identified by its ``isbn``
  number::

        {
            "isbn": 1,
            "title": "Dive into Python", 
            "author": "http://www.example.com/api/author/1"
        }

* **GET** ``author/`` -- Returns a list of authors that wrote the books in our
  library::

        [
            {
                "id": 1,
                "name": "Mark Pilgrim", 
                "resource_url": "http://www.example.com/api/author/1"
            },
            # ...
        ]

* **GET** ``author/{id}`` -- Returns a specific author, identified by its 
  ``id``::

        {
            "id": 1,
            "name": "Mark Pilgrim",
        }

* **POST** ``search/`` -- Searches the library and returns matching books::

        {
            "query": "Python"
        }

        [
            {
                "isbn": 1,
                "title": "Dive into Python", 
                "resource_url": "http://www.example.com/api/book/1"
            },
            # ...
        ]

Create a client
---------------

A typical client that can talk to a RESTful API using JSON, is no more then:

.. sourcecode:: python

    from restorm.clients.jsonclient import JSONClient
    
    client = JSONClient(root_uri='http://www.example.com/api/')
    
Since this tutorial uses a non-existant library API, the client doesn't work. We
can however mock its intended behaviour.

Create a mock API
-----------------

In order to test your client, you can emulate a whole API using the
``MockApiClient``. However, sometimes it's faster or easier to use a single, 
predefined response, using the ``MockClient``.

Since our library API is not that complex it is very straighforward to mock the
entire API, so we'll do just that. The ``MockApiClient`` takes two arguments.
The ``root_uri`` is the same as for regular clients but in addition, there is
the ``responses`` argument. The ``responses`` argument takes a ``dict`` of 
available resource URLs, supported methods, response headers and data. It's best
to just look at the example below to understand its structure.

The mock API below contains a list of books and a list of authors. To keep it 
simple, both list resources contain only 1 item:

.. sourcecode:: python

    from restorm.clients.mockclient import MockApiClient
    
    mock_client = MockApiClient(
        responses={
            'book/': {'GET': ({'Status': 200}, [{'isbn': 1, 'title': 'Dive into Python', 'resource_url': 'http://www.example.com/api/book/1'}])},
            'book/1': {'GET': ({'Status': 200}, {'isbn': 1, 'title': 'Dive into Python', 'author': 'http://www.example.com/api/author/1'})},
            'author/': {'GET': ({'Status': 200}, [{'id': 1, 'name': 'Mark Pilgrim', 'resource_url': 'http://www.example.com/author/1'}])},
            'author/1': {'GET': ({'Status': 200}, {'id': 1, 'name': 'Mark Pilgrim'})}
            'search/': {'POST': ({'Status': 200}, [{'isbn': 1, 'title': 'Dive into Python', 'resource_url': 'http://www.example.com/api/book/1'}])},
        },
        root_uri='http://www.example.com/api/'
    )

It's worth mentioning that you are not creating an API here, you are mocking it.
Simple and limited responses are usually fine. If the API would contain huge
responses, you can also use the ``FileResponse`` class to read the mock response
from a file.    
    
Define resources
----------------

We start with the most basic resource, the ``Author`` resource:

.. sourcecode:: python

    from restorm.resource import Resource
    
    class Author(Resource):
        class Meta:
            list = r'^author/$'
            item = r'^author/(?P<id>\d+)$'

We subclass ``Resource`` and add an inner ``Meta`` class. In the ``Meta`` class
we add two attributes that are internally used by the ``ResourceManager`` to
perform ``get`` and ``all`` operations:

* **list** -- The URL-pattern to retrieve the list of authors.
* **item** -- The URL-pattern to retrieve a specific author by ``id``.

For our ``Book`` resource, it's also possible to search for books. We can add 
this functionality with a custom ``ResourceManager``:

.. sourcecode:: python

    from restorm.resource import ResourceManager

    class BookManager(ResourceManager):
        def search(self, query, client=None):
            response = client.post('search/', '{ "query": "%s" }' % query)
            return response.content

No validation or exceptions in the request and response are handled in the above
example for readability reasons. In a production environment, you should.
            
We also need to define the ``Book`` resource itself and add our custom manager
by adding an instance of it to the ``objects`` attribute on the resource.

.. sourcecode:: python

    class Book(Resource):
    
        objects = BookManager()
        
        class Meta:
            list = r'^book/$'
            item = r'^book/(?P<isbn>\d)$'

Bringing it all together
------------------------

You can access the ``Book`` resource and the related ``Author`` resource using 
the ``mock_client``, or if the library API was real, use the ``client``. We can
pass the client to use as an argument to all manager functions (like ``get``, 
``all`` and also the ``search`` function we defined earlier).

.. sourcecode:: python

    >>> book = Book.objects.get(isbn=1, client=mock_client) # Get book with ISBN number 1.
    >>> book.data['title'] # Get the value of the key "name".
    u'Dive into Python'
    >>> book.data['author'] # Get the value of the key "author".
    u'http://www.example.com/api/author/1'
    >>> author = book.data.author # Perform a GET on the "author" resource.
    >>> author.data['name']
    u'Mark Pilgrim'

Our custom manager added a search function, let's use it:

.. sourcecode:: python

    >>> Book.objects.search(query='python', client=mock_client)
    [{'isbn': 1, 'title': 'Dive into Python', 'resource_url': 'http://www.example.com/api/book/1'}]

Since it's mocked, we could search for anything and the same response would come
back over and over.

.. note:: As you may have noticed, the response content contains actual Python 
    objects. The ``MockApiClient`` simply returns the content as is. If you 
    prefer using JSON, you can achieve the same behaviour with:

.. sourcecode:: python

        from restorm.clients.mockclient import BaseMockApiClient
        from restorm.clients.jsonclient import JSONClientMixin
        
        class MockJSONApiClient(BaseMockApiClient, JSONClientMixin):
            pass
            
        client = MockJSONApiClient(
            responses={
                # Note the difference. The content is now JSON.
                'book/1': {'GET': ({'Status': 200, 'Content-Type': 'application/json'}, '{"id": 1, "title": "Dive into Python", "author": "http://www.example.com/api/author/1"}',
                # ...
            },
            root_uri='http://www.example.com/api/'
        )
