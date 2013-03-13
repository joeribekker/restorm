import sys

from restorm.examples.mock.api import TicketApiClient


def main(argv):
    """
    Start with::
    
        python -m restorm.examples.mock.library_serv [port or address:port]

    """
    ip_address = '127.0.0.1'
    port = 8000

    # This is an example. Your should do argument checking.
    if len(argv) == 1:
        ip_address_port = argv[0].split(':', 1)
        if len(ip_address_port) == 1:
            port = ip_address_port[0]
        else:
            ip_address, port = ip_address_port 

    # Create a playground HTTP server that handles requests from the 
    # ``LibraryApiClient``.     
    api = TicketApiClient('http://%s:%s/api/' % (ip_address, port))
    server = api.create_server(ip_address, int(port))

    print 'Mock ticket webservice is running at http://%s:%s/api/' % (ip_address, port)
    print 'Quit the server with CTRL-C.'
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Closing server...'
        server.socket.close()


if __name__ == '__main__':
    main(sys.argv[1:])
