from restorm.examples.mock.api import LibraryApiClient


def main():
    ip_address = '127.0.0.1'
    port = 80

    # Create a playground HTTP server that handles requests from the 
    # ``LibraryApiClient``.     
    server = LibraryApiClient().create_server(ip_address, port)

    print 'Started mock library werbservice on %s:%s' % (ip_address, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print 'Closing server...'
        server.socket.close()


if __name__ == '__main__':
    main()
