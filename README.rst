RestClient
==========

Inspired by Django's ORM, **RestClient** allows you to interact with resources
as if they were objects.

Description
-----------

Most RESTful webservices are very easy to access with very little code.
**RestClient** is just a small layer on top of ``httplib2.Http`` to get a
response from a webservice. However, instead of regular Python ``dict``
objects, you'll get a ``dict``-like object that knows how to access related
resources as well.

Access a related resource::

    >>> book = Book.objects.get(id=1, client=jsonclient) # Get book with ID 1.
    >>> book['name'] # Get the value of the key "name".
    u'Dive Into Python'
    >>> book['author'] # Get the value of the key "author".
    http://api.example.com/author/3
    >>> author = book.author # Perform a GET on the "author" resource.
    >>> author['name']
    u'Mark Pilgrim'

Accessing multiple related resources::

    >>> city = City.objects.get(code='AMS')
    >>> city.country.continent['name'] # Perform 2 GET requests.
    u'Europe'

Install
-------



Contribute
----------

#. Get the code from Github::

    $ git clone git://github.com/joeribekker/restclient.git

#. Create and activate a virtual environment::

    $ cd restclient
    $ virtualenv .
    $ source bin/activate

#. Setup the project for development::

    $ python setup.py develop

#. Start hacking!

Tests
-----

Performing the unit tests::

    python restclient/tests/tests.py -v
