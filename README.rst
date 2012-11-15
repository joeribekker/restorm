RestORM
=======

RestORM allows you to interact with resources as if they were objects (object
relational mapping), mock entire webservices and incorporate custom client
logic.


Description
-----------

Most RESTful webservices are very easy to access with very little code.
RestORM is just a small layer on top of ``httplib2.Http`` to get a response 
from a webservice. However, instead of regular Python ``dict`` objects, you'll
get a ``dict``-like object that knows how to access related resources as well.

Until a version 1.0 release, backwards incompatible changes may be introduced
in future 0.x versions.

Features
--------

* Object relational mapping of webservice resources.
* Flexible client architecture that can be used with your own or third party
  clients (like oauth).
* Extensive mocking module allows you to mock webservice responses, or even 
  complete webservices.
* Examples for Twitter and Flickr API.

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
keep it simple, both lists contain only 1 item::

    from restorm.clients.mockclient import MockApiClient
    
    client = MockApiClient(
        responses={
            'book/': {
                'GET': ({'Status': 200}, [{'id': 1, 'title': 'Dive into Python', 'resource_url': 'http://www.example.com/api/book/1'}]),
                'POST': ({'Status': 201, 'Location': 'http://www.localhost/api/book/2'}, ''),
            },
            'book/1': {'GET': ({'Status': 200}, {'id': 1, 'title': 'Dive into Python', 'author': 'http://localhost/api/author/1'})},
            'author/': {'GET': ({'Status': 200}, [{'id': 1, 'name': 'Mark Pilgrim', 'resource_url': 'http://localhost/author/1'}])},
            'author/1': {'GET': ({'Status': 200}, {'id': 1, 'name': 'Mark Pilgrim'})}
        },
        root_uri='http://localhost/api/'
    )

Define resources
----------------

Setup your client side resource definitions::

    from restorm.resource import Resource
    
    class Book(Resource):
        class Meta:
            list = r'^book/$'
            item = r'^book/(?P<id>\d)$'

Make it work
------------

You can simply access the ``Book`` resource::

    >>> book = Book.objects.get(id=1, client=client) # Get book with ID 1.
    >>> book.data['title'] # Get the value of the key "name".
    u'Dive Into Python'
    >>> book.data['author'] # Get the value of the key "author".
    u'http://www.example.com/api/author/1'
    >>> author = book.data.author # Perform a GET on the "author" resource.
    >>> author.data['name']
    u'Mark Pilgrim'


.. note:: As you may have noticed, the response content contains actual Python 
    objects. The ``MockApiClient`` simply returns the content as is. If you 
    prefer using JSON, you can achieve the same behaviour with::
       
        from restorm.clients.mockclient import BaseMockApiClient
        from restorm.clients.jsonclient import JSONClientMixin
        
        class JSONMockApiClient(BaseMockApiClient, JSONClientMixin):
            pass
            
        client = JSONMockApiClient(
            responses={
                # Note the difference. The content is now JSON.
                'book/1': {'GET': ({'Status': 200, 'Content-Type': 'application/json'}, '{"id": 1, "title": "Dive into Python", "author": "http://localhost/api/author/1"}',
                # ...
            },
            root_uri='http://www.example.com/api/'
        )


Contribute
==========

#. Get the code from Github::

    $ git clone git://github.com/joeribekker/restorm.git

#. Create and activate a virtual environment::

    $ cd restorm
    $ virtualenv .
    $ source bin/activate

#. Setup the project for development::

    $ python setup.py develop

#. Start hacking!

Testing
=======

RestORM has a whooping 90% test coverage. Although reaching 100% is not a goal
by itself, I consider unit testing to be essential during development.

Performing the unit tests yourself::

    python setup.py test

