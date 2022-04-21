from urllib.parse import urlparse
import socket


def build_request_URL(host_addr: str, port_no: int, queries: str) -> str:
    return 'http://' + host_addr + ':' + str(port_no) + '/' + queries

def get_request_path(request_url: str):
    path_extract = urlparse(request_url).path

    if not path_extract:
        path = 'wiki/Main_Page'

    path = path_extract
    return path

def get_my_ip():
    '''
        Function: get_localhost_addr() - determines the localhost ip address by pinging to Google's primary DNS server
        Parameters: none
        Returns: the localhost ip address
    '''
    host_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_socket.connect(('8.8.8.8', 80))
    
    # returns the localhost name: (IP Address, Port No.)
    localhost = host_socket.getsockname()
    host_socket.close()

    return localhost[0]
    
def write_to_file(file_name: str, content: str) -> None:
    '''
        Function: write_to_file() - writes and saves content to a file
        Parameters: 
            file_name - the name of the file to write to; if file does not exist, it is created
            content - the content to be written to the file
        Returns: none
    '''
    try:
        file = open(file_name, 'w+')
        file.write(content)

    except IOError as io_error:
        raise io_error
    
    finally:
        file.close()    #type:ignore