.. image:: https://secure.travis-ci.org/joeribekker/restorm.png?branch=master
    :alt: Build Status
    :target: http://travis-ci.org/joeribekker/restorm

RestORM
=======

RestORM allows you to interact with resources as if they were objects (object
relational mapping), mock an entire API and incorporate custom client logic.

Description
-----------

Most RESTful API's are very easy to access with very little code. RestORM is 
just a small layer on top of ``httplib2.Http`` to get a response from an API.
However, instead of regular Python ``dict`` objects, you'll get a ``dict``-like
object that knows how to access related resources as well.

Until a version 1.0 release, backwards incompatible changes may be introduced
in future 0.x versions. Currently, RestORM works on Python 2.5+ with Python 3
support on its way.

Features
--------

* Object relational mapping of API resources (Django-like but does not depend on
  Django at all).
* Flexible client architecture that can be used with your own or third party
  clients (like oauth).
* Extensive mocking module allows you to mock API responses, or even 
  complete API's.
* Examples for Twitter and Flickr API.

Quick start
===========

This is a compressed version of the tutorial. The full documentation can be 
found `here <https://restorm.readthedocs.org>`_.

Create a client
---------------

A typical client that can talk to a RESTful API using JSON, is no more then:

.. sourcecode:: python

    from restorm.clients.jsonclient import JSONClient
    
    client = JSONClient(root_uri='http://www.example.com/api/')
    
Instead of this client, we mock its intended behaviour.
    
Create a mock API
-----------------

In order to test your client, you can emulate a whole API using the
``MockApiClient`` and add pre-defined responses.

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
        },
        root_uri='http://www.example.com/api/'
    )

Define resources
----------------

We start with our main resource, the ``Book`` resource as a subclass of 
``Resource``. Two attributes in the inner ``Meta`` class indicate a URL-pattern
how we can access all books (``list``) and a single book (``item``):

.. sourcecode:: python

    from restorm.resource import Resource

    class Book(Resource):
        class Meta:
            list = r'^book/$'
            item = r'^book/(?P<isbn>\d)$'

Bringing it all together
------------------------

You can access the ``Book`` resource and the (runtime created) related 
``Author`` resource using the ``mock_client``:

.. sourcecode:: python

    >>> book = Book.objects.get(isbn=1, client=mock_client) # Get book with ISBN number 1.
    >>> book.data['title'] # Get the value of the key "name".
    u'Dive into Python'
    >>> book.data['author'] # Get the value of the key "author".
    u'http://www.example.com/api/author/1'
    >>> author = book.data.author # Perform a GET on the "author" resource.
    >>> author.data['name']
    u'Mark Pilgrim'

Install
=======

RestORM is on PyPI so you can simply use::

    $ pip install restorm

If you want the latest development version, get the code from Github::

    $ git clone git://github.com/joeribekker/restorm.git
    $ cd restorm
    $ python setup.py install

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

    pip install nose
    python setup.py nosetest

