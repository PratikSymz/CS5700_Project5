import socket


def build_request_URL(host_addr: str, port_no: int, query: str) -> str:
    '''
        Function: build_request_URL() - this method is responsible for building HTTP request url based on the input path parameters
        Parameters: 
            host_addr - the url hostname
            port_no - the port number of the host
            query - url path query parameter
        Returns: concatenated url path string based on the input parameters
    '''
    return 'http://' + host_addr + ':' + str(port_no) + '/' + query

def get_my_ip() -> str:
    '''
        Function: get_my_ip() - determines the server's IP address by pinging to Google's primary DNS server
        Parameters: none
        Returns: the server's IP address
    '''
    host_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    host_socket.connect(('8.8.8.8', 80))
    
    # the localhost name: (IP Address, Port No.)
    localhost: tuple[str, int] = host_socket.getsockname()
    # close the socket
    host_socket.close()

    return localhost[0]
    
def write_to_file(file_name: str, content: bytes) -> None:
    '''
        Function: write_to_file() - writes and saves byte content to a file
        Parameters: 
            file_name - the name of the file to write to; if file does not exist, it is created
            content - the content (in bytes) to be written to the file
        Returns: none
    '''
    with open(file_name, 'wb+') as file:
        file.write(content)
