Clients
=======

At the heart of RestORM you have a ``Client``. The client simply allows you to
connect to an API and the one RestORM uses is built on top of the excellent
_`httplib2 library <http://code.google.com/p/httplib2/>`. However, you are free
to use any HTTP client library as long as you add the RestORM mixins.

Using different HTTP client libraries
-------------------------------------

There are lots of different client libraries. RestORM chose for ``httplib2`` as
default HTTP client library because it's an active project with built-in caching
and overall has the best performance.

Do not let the above stop you from using your own preferred HTTP client library
like _`requests <http://docs.python-requests.org/en/latest/>`,
_`oauth2 <http://pypi.python.org/pypi/oauth2/>`, or even 
_`httplib <http://docs.python.org/2/library/httplib.html>`

Example: OAuth
~~~~~~~~~~~~~~

Many API's use OAuth, an open standard for authorization. It's quite simple to
incorporate the _`oauth2 library <http://pypi.python.org/pypi/oauth2/>` in 
combination with one of the client mixins, for example the ``JSONClientMixin``
and override the ``request`` method to make a request using OAuth

.. sourcecode:: python

    import oauth2 as oauth
    from restorm.clients.jsonclient import JSONClientMixin

    class OauthClient(oauth.Client, JSONClientMixin):
        def request(self, uri, method='GET', body=None, headers=None, *args, **kwargs):
            # Create request.
            request = self.create_request(uri, method, body, headers)

            # Perform request.
            response_headers, response_content = super(OauthClient, self).request(request.uri, request.method, request.body, request, *args, **kwargs)
            
            # Create response.
            return self.create_response(response_headers, response_content, request)

Once we have this, we can 
            
>>> consumer = oauth.Consumer(key='YOUR_KEY', secret='YOUR_SECRET')
>>> token = oauth.Token(key='YOUR_TOKEN', secret='YOUR_TOKEN_SECRET')
>>> client = OauthClient(consumer, token)

