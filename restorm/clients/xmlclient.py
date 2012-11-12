from restorm.clients.base import ClientMixin, BaseClient


XML_LIBRARY_FOUND = True
try:
    from lxml import etree
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
                except ImportError:
                    XML_LIBRARY_FOUND = False


class XMLClientMixin(ClientMixin):
    MIME_TYPE = 'application/xml'

    def create_request(self, uri, method, body=None, headers=None):
        if headers is None:
            headers = {}

        headers.update({
            'Accept': self.MIME_TYPE,
            'Content-Type': self.MIME_TYPE,
        })
        
        return super(XMLClientMixin, self).create_request(uri, method, body, headers)

    def create_response(self, response_headers, response_content, request):
        response = super(XMLClientMixin, self).create_response(response_headers, response_content, request)

        if 'Content-Type' in response and response['Content-Type'].startswith(self.MIME_TYPE):
            response.content = etree.fromstring(response.content)
            
        return response

    def get(self, uri):
        return super(XMLClientMixin, self).get(uri)

    def post(self, uri, data):
        if isinstance(data, etree.Element):
            data = etree.tostring(data)
        return super(XMLClientMixin, self).post(uri, data)

    def put(self, uri, data):
        if isinstance(data, etree.Element):
            data = etree.tostring(data)
        return super(XMLClientMixin, self).put(uri, data)

    def delete(self, uri):
        return super(XMLClientMixin, self).delete(uri)


class XMLClient(BaseClient, XMLClientMixin):
    """
    Client that handles XML requests and responses.
    """
    def __init__(self, *args, **kwargs):
        if not XML_LIBRARY_FOUND:
            raise ImportError('Could not load any known XML library.')
        super(XMLClient, self).__init__(*args, **kwargs)
