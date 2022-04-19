import os, socket, sys, getopt, errno, urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import BaseServer

import utils


PORT_SERVER: int = 8080
RESPONSE_OK: int = 200

class HTTPManager(BaseHTTPRequestHandler):
    def __init__(self, origin_addr: str, port: int, cache: list, *args) -> None:
        self.origin_addr = origin_addr
        self.port = port
        self.mem_cache = cache

        # Make origin server socket connection
        try:
            self.origin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.origin_socket.connect((self.origin_addr, PORT_SERVER))
        except:
            sys.exit('Origin socket connection failed...')
        super().__init__(*args)

    def do_GET(self) -> None:
        ''' Implement basic caching technique. If file in cache, send client the file. Else, retrieve file from origin server '''
        if self.path not in self.mem_cache:
            try:
                request_url = utils.build_request_URL(self.origin_addr, self.port, self.path)
                response = urllib.request.urlopen(request_url)

            except Exception as network_exception:
                print(str(network_exception))
                return

            self.send_response(RESPONSE_OK)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response.read())

        else:
            cached_file = open(os.pardir + self.path)
            self.send_response(RESPONSE_OK)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(cached_file.read().encode())
            cached_file.close()

    def store_in_local(self, path: str, contents: str) -> None:
        path_name = os.pardir + path
        
        path_directory = os.path.dirname(path_name)
        if not os.path.exists(path_directory):
            os.makedirs(path_directory)

        # Append to the cache
        try:
            utils.write_to_file(path_name, contents)
            self.mem_cache.append(path)
        except IOError as cache_error:
            print(cache_error)
            # Cache is full, no more appends
            # Remove path from the mem_cache and the local cache directory
            if cache_error == errno.EDQUOT:
                self.mem_cache.remove(path)
                os.remove(path_name)


class HTTPServer(BaseServer):
    def __init__(self, server_address: tuple[str, int], RequestHandlerClass) -> None:
        super().__init__(server_address, RequestHandlerClass)
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
            self.server_socket.bind(self.server_address)
            self.server_socket.listen(30)    # At most 30 connect requests
        except:
            sys.exit('Server socket connection failed...')

def run_server(origin_server_addr: str, port: int) -> None:
    cache = []

    http_manager = HTTPManager(origin_server_addr, port, cache)
    http_server = HTTPServer(('', port), http_manager)  # type: ignore
    http_server.serve_forever()


if __name__ == "__main__":
    opts, argvs = getopt.getopt(sys.argv[1: ], 'p:o:')
    for opt, arg in opts:
        if opt == '-p':
            port = int(arg)
        elif opt == '-o':
            server_name = arg
        else:
            sys.exit('FORMAT: ./httpserver -p <port> -o <origin>')

    run_server(server_name, port)   #type:ignore
