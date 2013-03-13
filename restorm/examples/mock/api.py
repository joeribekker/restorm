"""
.. note:: This example is also used in internal unit tests. The 
   ``MockApiClient`` and related classes are specifically made for the purpose
   of unit testing, or "playground" testing.

The example here is a JSON webservice. You can instantiate it and perform 
requests from the console:

>>> from restorm.examples.mock.api import LibraryApiClient
>>> client = LibraryApiClient()
>>> response = client.get('author/1')
>>> response.raw_content
'{"books": [{"resource_url": "http://localhost/api/book/978-1441413024", "isbn": "978-1441413024", "title": "Dive into Python"}], "id": 1, "name": "Mark Pilgrim"}'

You can also start it as a server and connect to it with your browser, or let
your application connect to it::

    $ python -m restorm.examples.mock.library_serv 127.0.0.1:8000
    
Shut it down with CTRL-C. The above Python script basically does:

>>> server = client.create_server()
>>> server.serve_forever()

"""
from restorm.clients.jsonclient import JSONClientMixin, json
from restorm.clients.mockclient import BaseMockApiClient


class LibraryApiClient(BaseMockApiClient, JSONClientMixin):
    """
    Mock library webservice containing books and authors.

    .. note:: This is a very inconsistent webservice. All resources are for
       demonstration purposes and show different kinds of ReST structures.

    """
    def __init__(self, root_uri=None):
        # Creating a mock server from this MockApiClient, related resource 
        # URI's need to show the same IP address and port.
        if not root_uri:
            root_uri = 'http://localhost/api/'

        responses = {
            # The index.
            '': {
                'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                    [{
                        'description': 'List of books.',
                        'resource_url': '%sbook/' % root_uri
                    }, {
                        'description': 'List of authors.',
                        'resource_url': '%sauthor/' % root_uri
                    }, {
                        'description': 'Search in our database',
                        'resource_url': '%ssearch/' % root_uri
                    }])
                )
            },
            # Book list view contains a ``list`` of ``objects`` representing a
            # (small part of the) book.
            'book/': {
                'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                    [{
                        'isbn': '978-1441413024',
                        'title': 'Dive into Python',
                        'resource_url': '%sbook/978-1441413024' % root_uri
                    }, {
                        'isbn': '978-1590597255',
                        'title': 'The Definitive Guide to Django',
                        'resource_url': '%sbook/978-1590597255' % root_uri
                    }])
                )
            },
            # Book item view contains a single ``object`` representing a book,
            # including (in addition to the list view) the author resource,
            # ISBN and subtitle.
            'book/978-1441413024': {
                'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                    {
                        'isbn': '978-1441413024',
                        'title': 'Dive into Python',
                        'subtitle': None,
                        'author': '%sauthor/1' % root_uri
                    })
                )
            },
            'book/978-1590597255': {
                'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                    {
                        'isbn': '978-1590597255',
                        'title': 'The Definitive Guide to Django',
                        'subtitle': 'Web Development Done Right',
                        'author': '%sauthor/2' % root_uri
                    })
                )
            },
            # Author list view contains an ``object`` with a single item
            # containing the ``list`` of ``objects``. This, in contrast to the
            # list view of books, which contains a ``list`` as root element.
            'author/': {
                'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                    {
                        'author_set': [{
                            'id': 1,
                            'name': 'Mark Pilgrim',
                            'resource_url': '%sauthor/1' % root_uri
                        }, {
                            'id': 2,
                            'name': 'Jacob Kaplan-Moss',
                            'resource_url': '%sauthor/2' % root_uri
                        }]
                    })
                )
            },
            # Author item view. Contains a nested list of all books the author
            # has written.
            'author/1': {
                'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                    {
                        'id': 1,
                        'name': 'Mark Pilgrim',
                        'books': [{
                            'isbn': '978-1441413024',
                            'title': 'Dive into Python',
                            'resource_url': '%sbook/978-1441413024' % root_uri
                        }]
                    })
                )
            },
            'author/2': {
                'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                    {
                        'id': 2,
                        'name': 'Jacob Kaplan-Moss',
                        'books': [{
                            'isbn': '978-1590597255',
                            'title': 'The Definitive Guide to Django',
                            'resource_url': '%sbook/978-1590597255' % root_uri
                        }]
                    })
                )
            },
            # Ofcourse, it doesn't matter what you sent to this resource, the
            # results will always be the same.
            'search/': {
                'POST': ({'Status': 200, 'Content-Type': 'application/json', 'X-Cache': 'MISS'}, json.dumps(
                    {
                        'meta': {
                            'query': 'Python',
                            'total': 1,
                        },
                        'results': [{
                            'isbn': '978-1441413024',
                            'title': 'Dive into Python',
                            'resource_url': '%sbook/978-1441413024' % root_uri
                        }]
                    })
                )
            }
        }
        super(LibraryApiClient, self).__init__(responses=responses, root_uri=root_uri)


class TicketApiClient(BaseMockApiClient, JSONClientMixin):
    """
    Mock issue ticket API.

    .. note:: This is a very inconsistent webservice. All resources are for
       demonstration purposes and show different kinds of ReST structures.

    """
    def __init__(self, root_uri=None):
        # Creating a mock server from this MockApiClient, related resource
        # URI's need to show the same IP address and port.
        if not root_uri:
            root_uri = 'http://localhost/api/'

        responses = {
            # Issue list view contains a ``list`` of ``objects``.
            'issue/': {
                'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                    [{
                         'id': 1,
                         'title': 'Cannot update an issue',
                         'resource_url': '%sissue/1' % root_uri
                     }, {
                         'id': 2,
                         'title': 'Cannot create an issue',
                         'resource_url': '%sissue/2' % root_uri
                     }])
                ),
                'POST': ({'Status': 201, 'Content-Type': 'application/json', 'Location': '%sissue/2' % root_uri}, json.dumps(''))
            },
            # Issue item view contains a single ``object`` representing an issue.
            'issue/1': {
                'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                    {
                        'id': 1,
                        'title': 'Cannot update an issue',
                        'description': 'This needs more work.',
                    })
                )
            },
            'issue/2': {
                'GET': ({'Status': 200, 'Content-Type': 'application/json'}, json.dumps(
                    {
                        'id': 2,
                        'title': 'Cannot create an issue',
                        'description': 'This needs more work.',
                    })
                ),
                'PUT': ({'Status': 204, 'Content-Type': 'application/json'}, json.dumps(''))
            },
        }
        super(TicketApiClient, self).__init__(responses=responses, root_uri=root_uri)
