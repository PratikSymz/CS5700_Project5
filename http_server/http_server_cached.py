import csv, os, socket, argparse, sys, zlib, time
from typing import Tuple

from http.server import HTTPServer, BaseHTTPRequestHandler
import requests

import utils


CACHE_LIMIT: int = 20000000      # Cache size/CDN server limit: 20MB

''' Constant set of fields to use in HTTP request headers '''
CONTENT_TYPE_HEADER: str = 'Content-type'
CONTENT_TYPE: str = 'text/html'

# MAX Message Buffer length
BUFFER_SIZE: int = 4096

# Message encode and decode format
FORMAT: str = 'utf-8'

class CacheManager:
    def __init__(self, origin_addr='', origin_port=0):
        self.origin_addr = origin_addr
        self.origin_port = origin_port

        # The CDN server cache
        self.CACHE: dict = {}

        # Load the popularity data in the cache directory
        self.load_popularity_data()

    def load_popularity_data(self) -> bool:
        ''' Load popularity rates and the corresponding search query from the CSV file '''
        ''' Params: none, Returns: boolean (successful or not) '''
        # Open CSV file
        with open('http_server/pageviews_modded.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file, quotechar='"', delimiter=',')
            # Read line items
            for line_item in csv_reader:
                '''
                Re: CSV file Format, there are two escape mechanisms you need to be aware of:
                    If a field contains a , character, the whole field is escaped between a pair of " characters.
                    If a "-escaped field internally contains a "character, the internal" character is expanded to "".
                '''
                if (self.get_cache_size(self.CACHE) < CACHE_LIMIT):
                    # Download data from the origin server and save it in the cache in order of the popularity hits
                    # Build the origin server GET request url
                    origin_request_url = utils.build_request_URL('cs5700cdnorigin.ccs.neu.edu', 8080, line_item[0])
                    # Send GET request to the origin server and receive response
                    response = requests.get(origin_request_url)
                    
                    # Check for content not found
                    if (response.status_code == 200):
                        # Compress and cache the origin server's response
                        compressed_response = zlib.compress(response.content)

                        # Check if adding a file to the cache overloads the memory
                        if (self.get_cache_size(self.CACHE) + len(compressed_response) > CACHE_LIMIT):
                            break

                        self.CACHE[line_item[0]] = compressed_response  # bytes
        
        return True

    def get_cache_size(self, obj, seen=None):
        ''' Referred from: https://gist.github.com/bosswissam/a369b7a31d9dcab46b4a034be7d263b2#file-pysize-py '''
        ''' Recursively find the size of cache objects '''
        size = sys.getsizeof(obj)
        if seen is None:
            seen = set()
        obj_id = id(obj)
        if obj_id in seen:
            return 0

        # Important mark as seen *before* entering recursion to gracefully handle
        # self-referential objects
        seen.add(obj_id)
        if isinstance(obj, dict):
            size += sum([self.get_cache_size(v, seen) for v in obj.values()])
            size += sum([self.get_cache_size(k, seen) for k in obj.keys()])
        elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
            size += sum([self.get_cache_size(i, seen) for i in obj])
            if hasattr(obj, '__dict__'):
                size += self.get_cache_size(obj.__dict__.values(), seen)
        elif hasattr(obj, '__dict__'):
            size += self.get_cache_size(obj.__dict__, seen)
        return size


class CDNHTTPRequestHandler(BaseHTTPRequestHandler):
    # Initialize the LRU cache
    global cm
    cm = CacheManager()
    
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
        # Check if current path url in cache
        try:
            # Validate the path
            if (self.path == '/grading/beacon'):
                # Build the HTTP response headers
                self.send_response(204)
                self.send_header(CONTENT_TYPE_HEADER, CONTENT_TYPE)
                self.end_headers()
                # Send the empty response to the client
                self.wfile.write(b'')   # ! Send something
            
            else:
                print(self.path)
                print(self.path.split('/'))

                if (len(self.path.split('/')) > 2):
                    self.send_error(400, 'Bad request')    # Bad Request

                query = self.path.split('/')[-1]
                global cm

                if query in cm.CACHE.keys():
                    # Extract the cached response
                    cached_response = cm.CACHE.get(query)   # Compressed
                    response = zlib.decompress(cached_response)

                    # Build the HTTP response headers
                    self.send_response(200)
                    self.send_header(CONTENT_TYPE_HEADER, CONTENT_TYPE)
                    self.end_headers()
                    # Send the cached response to the client
                    self.wfile.write(response)  # ! Check this

                # Current path url not in cache
                else:
                    # Build the origin server GET request url
                    origin_request_url = utils.build_request_URL('cs5700cdnorigin.ccs.neu.edu', 8080, query)
                    # Send GET request to the origin server and receive response
                    response = requests.get(origin_request_url)
                    
                    # Check for content not found
                    if (response.status_code != 200):
                        self.send_error(404, 'Not Found')    # Not found
                    
                    else:
                        # Decode the origin server response
                        origin_response = response.content  # text/HTML

                        # Build the HTTP response headers
                        self.send_response(200)
                        self.send_header(CONTENT_TYPE_HEADER, CONTENT_TYPE)
                        self.end_headers()
                        # Send the origin response to the client
                        self.wfile.write(origin_response)

        except requests.exceptions.RequestException as error:
            raise(error)


def start_CDN_server() -> None:
    # Setup the CDN server
    my_IP = utils.get_my_ip()
    print(my_IP)
    http_server = HTTPServer((my_IP, 8080), CDNHTTPRequestHandler)
    # Activate the CDN server
    http_server.serve_forever()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='HTTP Server')
    # parser.add_argument('-p', dest='http_port', type=int)
    # parser.add_argument('-o', dest='origin_hostname', type=str)
    # args = parser.parse_args()

    start_CDN_server()