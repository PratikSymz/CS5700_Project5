import csv, os, socket, argparse
from email.policy import HTTP
from typing import Tuple

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import BaseServer
import urllib.request as urllib_req
import urllib.error as urllib_err
import requests

import utils

from cache_manager import CacheManager


CACHE_LIMIT: int = 20000000      # Cache size/CDN server limit: 20MB
RESP_SUCCESS: int = 200           # HTTP Response 200
ORIGIN_PORT: int = 8080

''' Constant set of fields to use in HTTP request headers '''
CONTENT_TYPE_HEADER: str = 'Content-type'
CONTENT_TYPE: str = 'text/html'

# MAX Message Buffer length
BUFFER_SIZE: int = 4096

# Message encode and decode format
FORMAT: str = 'utf-8'


class CDNHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        ''' CDN HTTP Handler:
            1. If query path IN cache
                return the cached response
            
            2. If query path NOT IN cache
                a. Send GET request to the ORIGIN server and receive response
                b. Cache the results IF:
                    Current cache size < CACHE LIMIT (20MB) and size(Wiki query HTML) < Available Cache space
                c. Otherwise, evict the least recently accessed item from the LRU cache tracker and the local cache dir.
                    Add the new item to the local cache dir and the LRU cache dir
        '''
        self.origin_addr: str = 'cs5700cdnorigin.ccs.neu.edu'
        self.origin_port: int = 8080
        
        origin_request_url = utils.build_request_URL(self.origin_addr, self.origin_port, self.path)
        print(self.path)
        # Send GET request to the origin server and receive response
        response = requests.get(origin_request_url)
        print(response.url)

        print(response.status_code)

        # Build the HTTP response headers
        self.send_response(RESP_SUCCESS)
        self.send_header(CONTENT_TYPE_HEADER, CONTENT_TYPE)
        self.end_headers()
        # Send the origin response to the client
        self.wfile.write(response.content)


def start_CDN_server(cdn_port: int, origin_hostname: str) -> None:
    # Setup the CDN HTTP request handler
 
    # Setup the CDN server
    my_IP = utils.get_my_ip()
    print(my_IP)
    http_server = HTTPServer((my_IP, cdn_port), CDNHTTPRequestHandler)
    # Activate the CDN server
    http_server.serve_forever()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='HTTP Server')
    # parser.add_argument('-p', dest='http_port', type=int)
    # parser.add_argument('-o', dest='origin_hostname', type=str)
    # args = parser.parse_args()

    #start_CDN_server(args.http_port, args.origin_hostname)
    manager = CacheManager()
