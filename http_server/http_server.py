import socket, argparse, sys

class HTTP_Server:

    """ Initiate socket connection """
    def __init__(self):
        try:
            # Set up Socket
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # TCP. IF UDP -> SOCK_DGRAM
            
            # Connect with socket
            # addr = BASE_URL, PORT_NO
            # client_socket.connect(addr)
        except:
            # Can't connect with socket
            # utils.close_stream(WebCrawler.client_socket_ssl)
            sys.exit("Can't connect with socket! Timeout " + "\n")

""" Script argument parser """
if __name__ == "__main__":
    parser = argparse.ArgumentParser('Project 5: Roll Your Own CDN')

    # Port Number: Optional argument
    parser.add_argument('-p', action='store', type=int, dest='PORT', help='<-p port>')
    # SSL, Hostname and NEUID: Mandatory
    parser.add_argument('-s', action='store_true', dest='SSL', required=True, help='<-s>')   # Store True value as default; Required on optional tag
    parser.add_argument('HOST', action='store', type=str, help='[hostname]')    # Store value from input
    parser.add_argument('NEU_USERNAME', action='store', type=str, help='[NEU ID]')     # Store value from input


    args = parser.parse_args()
    # Pass args to start() methods