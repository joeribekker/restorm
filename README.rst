=======
RestORM
=======

Inspired by Django's ORM, **RestORM** allows you to interact with resources
as if they were objects.

Description
===========

Most RESTful webservices are very easy to access with very little code.
**RestORM** is just a small layer on top of ``httplib2.Http`` to get a
response from a webservice. However, instead of regular Python ``dict``
objects, you'll get a ``dict``-like object that knows how to access related
resources as well.

Features
--------

* Object relational mapping of webservice resources.
* Flexible client architecture that can be used with your own or third party
  clients (like oauth).
* Extensive mocking module allows you to mock webservice responses, or even 
  complete webservices.


Getting started
===============

Create a mock webservice
------------------------

In order to test your client, you can emulate a whole webservice using the
``MockApiClient``. However, sometimes it's faster or easier to use a single, 
predefined response, using the ``MockClient`` and ``MockResponse`` 
(sub)classes.

You can also use ``FileResponse`` class to return the contents of a file as 
response in combination with the ``MockApiClient``.

The mock webservice below contains a list of books and a list of authors. To 
keep it simple, both lists contain only 1 items::

    client = MockApiClient(
        responses={
            '/api/book/': {
                'GET': ({'Status': 200}, [{'id': 1, 'name': 'Dive into Python', 'resource_url': 'http://www.example.com/api/book/1'}]),
                'POST': ({'Status': 201, 'Location': 'http://www.example.com/api/book/2'}, ''),
            },
            '/api/book/1': {'GET': ({'Status': 200}, {'id': 1, 'name': 'Dive into Python', 'author': 'http://www.example.com/api/author/1'})},
            '/api/author/': {'GET': ({'Status': 200}, [{'id': 1, 'name': 'Mark Pilgrim', 'resource_url': 'http://www.example.com/api/author/1'}])},
            '/api/author/1': {'GET': ({'Status': 200}, {'id': 1, 'name': 'Mark Pilgrim'})}
        },
        root_uri='http://www.example.com'
    )

Define resources
----------------

Setup your client side resource definitions::

    class Book(Resource):
        class Meta:
            list = (r'^book/$', 'book_set')
            item = r'^book/(?P<id>\d)$'
            root = 'http://www.example.com/api/'

Make it work
------------

You can simply access the ``Book`` resource::

    >>> book = Book.objects.get(id=1, client=client) # Get book with ID 1.
    >>> book.data['name'] # Get the value of the key "name".
    u'Dive Into Python'
    >>> book.data['author'] # Get the value of the key "author".
    u'http://www.example.com/api/author/1'
    >>> author = book.data.author # Perform a GET on the "author" resource.
    >>> author.data['name']
    u'Mark Pilgrim'


.. note:: As you may have noticed, the response content contains actual Python 
    objects. The ``MockApiClient`` simply returns the content as is. If you 
    prefer using JSON, you can achieve the same behaviour with::
       
        class JSONMockApiClient(BaseMockApiClient, JSONClientMixin):
            pass
            
        client = JSONMockApiClient(
            responses={
                # Note the difference. The content is now JSON.
                'book/1': {'GET': ({'Status': 200, 'Content-Type': 'application/json'}, '{"id": 1, "name": "Dive into Python", "author": "http://www.example.com/api/author/1"}',
                # ...
            },
            root_uri='http://www.example.com/api/'
        )


Install
=======

It's not yet in PyPI. If you want to use it in your project, you should know 
that this is still a work in progress and you probably know what to do.


Contribute
==========

#. Get the code from Github::

    $ git clone git://github.com/joeribekker/restclient.git

#. Create and activate a virtual environment::

    $ cd restclient
    $ virtualenv .
    $ source bin/activate

#. Setup the project for development::

    $ python setup.py develop

#. Start hacking!

Testing
=======

Performing the unit tests::

    python setup.py test

