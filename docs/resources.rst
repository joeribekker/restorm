Resources
=========

REST-style architectures consist of :doc:`clients` and servers. Clients 
initiate requests to servers; servers process requests and return appropriate 
responses. Requests and responses are built around the transfer of 
representations of :doc:`resources`. A resource can be essentially any coherent
and meaningful concept that may be addressed. A representation of a resource is
typically a document that captures the current or intended state of a resource.

In RestORM, a ``Resource`` is the single, definitive source of data about a
specific API endpoint. It contains the essential properties and behaviors of the
data you're accessing. Generally, each resource maps to a single API endpoint.

Defining resources
------------------
    
Imagine a RESTful library API, like described in the :doc:`tutorial` and the
:doc:`mocking` part of this documentation. You can request a list of books in
the library and a list of authors. The API provides data about a specific book,
like its title and author. To represent the book on our client side, we define
a ``Book`` resource that inherits from ``Resource``.

We also define an inner ``Meta`` class that contains meta properties about the 
book resource. It contains for example an attribute ``item`` that holds a 
relative URL pattern for retrieving a single book.

.. sourcecode:: python

    from restorm.resource import Resource

    class Book(Resource):
        class Meta:
            item = r'^book/(?P<isbn>\w+)$'
            
The ``item`` attribute holds a URL pattern that is a regular expression
describing on what URL a single book representation can be retrieved. The ``r``
in front of the string in Python means to take the string "raw" and nothing
should be escaped.

In Python regular expressions, the syntax for named regular-expression groups is
``(?P<name>pattern)``, where ``name`` is the name of the group and ``pattern``
is some pattern to match. In the example above the name ``isbn`` can be any word
of any length. A valid relative URL would be: ``book/1`` or ``book/abc123``.
            
As you may have noticed, nothing is said about the book's representation. There
is no strict definition of what should be a book. The server decides this for
you, or you can manually pass in data. All information passed to the 
``Resource`` constructor as first argument, is available in the ``data``
attribute.

.. sourcecode:: python

    >>> book = Book({'title': 'Hello world', 'subtitle': 'A good start'})
    >>> book.absolute_url
    None
    >>> book
    <Book: None>
    >>> book.data['title']
    'Hello world'

You can add any custom function to your resource class to help you work with the
data representation.

.. sourcecode:: python

    from restorm.resource import Resource

    class Book(Resource):
        class Meta:
            item = r'^book/(?P<isbn>\w+)$'
            
        @property
        def full_title(self):
            return '%s: %s' % (self.data['title'], self.data['subtitle'])

    >>> book = Book({'title': 'Hello world', 'subtitle': 'A good start'})
    >>> book.full_title
    'Hello world: A good start'
            
The default representation of a ``Resource`` is the class name followed by the
(absolute) URL of the retrieved representation, in the example there was none
so the value is ``None``.

You can override this with the ``__unicode__`` function:

.. sourcecode:: python

    class Book(Resource):
        # ...
    
        def __unicode__(self):
            if 'title' in self.data:
                return self.data['title']
            else:
                return '(unknown title)'

    >>> book = Book({'title': 'Hello world', 'subtitle': 'A good start'})
    >>> book.absolute_url
    None
    >>> book
    <Book: Hello world>

Resource managers
-----------------

A ``ResourceManager`` is the interface through which API requests can be 
performed on a ``Resource``. At least one manager exists for every resource.

By default, RestORM adds a ``ResourceManager`` with the name ``objects`` to 
every RestORM resource class.

Let's assume we already have a client ready, as described in :doc:`clients` but
we use our mock client so you can test the demonstrated code snippets yourself.

    >>> from restorm.examples.mock.api import LibraryApiClient
    >>> client = LibraryApiClient()

Our ``Book`` resource already allows us to get a single book from the library
API:

.. sourcecode:: python

    >>> book = Book.objects.get(isbn=1, client=client)
    >>> book.data['title']
    u'Dive into Python'

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

.. autoclass:: restorm.resource.ResourceManager
    :members: get, all, options

Related resources
-----------------

You can access all API resources by creating a ``Resource`` class for each API
resource.

.. sourcecode:: python

    class Author(Resource):
        class Meta:
            item = r'^author/(?P<id>\d+)$'

    >>> book = Book.objects.get(isbn=1)
    >>> book.data['author']
    u'http://www.example.com/api/author/1'
    >>> author = Author.objects.get(uri=book.data['author'])
    >>> author.data['name']
    u'Mark Pilgrim'
    
RestORM is aware of the API endpoint URL in the book resource. We can simply do:

.. sourcecode:: python

    >>> book = Book.objects.get(isbn=1)
    >>> book.data.author.data['name']
    u'Mark Pilgrim'

Even if we did not define the ``Author`` resource, the above would be valid. A
generic resource is then used to represent the author.
