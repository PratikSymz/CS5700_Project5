import os, socket, sys, argparse, errno, urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import BaseServer

import http_server.utils as utils


PORT_SERVER: int = 8080
RESPONSE_OK: int = 200

class HTTPManager(BaseHTTPRequestHandler):
    def __init__(self, origin_tuple: tuple[str, int], cache: list, *args) -> None:
        self.origin_addr = origin_tuple[0]
        self.port = origin_tuple[1]
        self.mem_cache = cache

        # Make origin server socket connection
        try:
            self.origin_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.origin_socket.connect((self.origin_addr, PORT_SERVER))
        except:
            sys.exit('Origin socket connection failed...')
        BaseHTTPRequestHandler.__init__(self, *args)


    def do_GET(self) -> None:
        ''' Implement basic caching technique. If file in cache, send client the file. Else, retrieve file from origin server '''
        if self.path not in self.mem_cache:
            try:
                request_url = utils.build_request_URL(self.origin_addr, self.port, self.path)
                response = urllib.request.urlopen(request_url)

                # Build local cache path for the url
                response_path = utils.get_request_path(request_url)
                # Retrieve data from the Origin server

            except Exception as network_exception:
                print(str(network_exception))
                return

            self.send_response(RESPONSE_OK)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            data = response.read().decode('utf-8')
            self.wfile.write(data)
            self.store_in_local(self.path, data)
            self.mem_cache.append(self.path)

        else:
            cached_file = open(os.pardir + self.path)
            self.send_response(RESPONSE_OK)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(cached_file.read().encode('utf-8'))
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
    def __init__(self, server_address: tuple[str, int], request_handler_class) -> None:
        BaseServer.__init__(self, server_address, request_handler_class)
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 2)
            self.server_socket.bind(self.server_address)
            self.server_socket.listen(30)    # At most 30 connect requests
        except:
            sys.exit('Server socket connection failed...')

def run_server(origin_server_addr: str, port: int) -> None:
    cache = []
    def handler(*args):
        HTTPManager((origin_server_addr, port), cache, *args)
    
    http_server = HTTPServer(('', port), handler)  # type: ignore
    http_server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('-p', dest='port', type=int)
    parser.add_argument('-o', dest='origin')
    args = parser.parse_args()

    run_server(args.origin, args.port)