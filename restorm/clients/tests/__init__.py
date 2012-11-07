from clients.mockclient import MockApiClient


class LibraryApiClient(MockApiClient):
    """
    Mock library webservice containing books and authors.

    NOTE: This is a very inconsistent webservice. All resources are for
    demonstration purposes and show different kinds of ReST structures.
    """
    def __init__(self):
        root_uri = 'http://www.example.com/api/'
        responses = {
            # Book list view contains a ``list`` of ``objects`` representing a
            # (small part of the) book.
            'book/': {
                'GET': ({'Status': 200},
                    [{
                        'isbn': '978-1441413024',
                        'title': 'Dive into Python',
                        'resource_url': 'http://www.example.com/api/book/978-1441413024'
                    }, {
                        'isbn': '978-1590597255',
                        'title': 'The Definitive Guide to Django',
                        'resource_url': 'http://www.example.com/api/book/978-1590597255'
                    }]
                )
            },
            # Book item view contains a single ``object`` representing a book,
            # including (in addition to the list view) the author resource,
            # ISBN and subtitle.
            'book/978-1441413024': {
                'GET': ({'Status': 200},
                    {
                        'isbn': '978-1441413024',
                        'title': 'Dive into Python',
                        'subtitle': None,
                        'author': 'http://www.example.com/api/author/1'
                    }
                )
            },
            'book/978-1590597255': {
                'GET': ({'Status': 200},
                    {
                        'isbn': '978-1590597255',
                        'title': 'The Definitive Guide to Django',
                        'subtitle': 'Web Development Done Right',
                        'author': 'http://www.example.com/api/author/2'
                    }
                )
            },
            # Author list view contains an ``object`` with a single item
            # containing the ``list`` of ``objects``. This, in contrast to the
            # list view of books, which contains a ``list`` as root element.
            'author/': {
                'GET': ({'Status': 200},
                    {
                        'author_set': [{
                            'id': 1,
                            'name': 'Mark Pilgrim',
                            'resource_url': 'http://www.example.com/api/author/1'
                        }, {
                            'id': 2,
                            'name': 'Jacob Kaplan-Moss',
                            'resource_url': 'http://www.example.com/api/author/2'
                        }]
                    }
                )
            },
            # Author item view. Contains a nested list of all books the author
            # has written.
            'author/1': {
                'GET': ({'Status': 200},
                    {
                        'id': 1,
                        'name': 'Mark Pilgrim',
                        'books': [{
                            'isbn': '978-1441413024',
                            'title': 'Dive into Python',
                            'resource_url': 'http://www.example.com/api/book/978-1441413024'
                        }]
                    }
                )
            },
            'author/2': {
                'GET': ({'Status': 200},
                    {
                        'id': 2,
                        'name': 'Jacob Kaplan-Moss',
                        'books': [{
                            'isbn': '978-1590597255',
                            'title': 'The Definitive Guide to Django',
                            'resource_url': 'http://www.example.com/api/book/978-1590597255'
                        }]
                    }
                )
            },
            # Ofcourse, it doesn't matter what you sent to this resource, the
            # results will always be the same.
            'search/': {
                'POST': ({'Status': 200, 'X-Cache': 'MISS'},
                    {
                        'meta': {
                            'query': 'Python',
                            'total': 1,
                        },
                        'results': [{
                            'isbn': '978-1441413024',
                            'title': 'Dive into Python',
                            'resource_url': 'http://www.example.com/api/book/978-1441413024'
                        }]
                    }
                )
            }
        }
        super(LibraryApiClient, self).__init__(responses=responses, root_uri=root_uri)