

def build_request_URL(host_addr: str, port_no: int, queries: str) -> str:
    return 'http://' + host_addr + ':' + str(port_no) + queries
    
def write_to_file(file_name: str, content: str):
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