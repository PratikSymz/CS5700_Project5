import argparse
import dnslib
import socket
import sys

class DNSServer:
    def __init__(self, args):
        # Command line arguments
        self.PORT = int(args.PORT)
        self.NAME = args.NAME

        self.BUFFER = 1024

        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except Exception as e:
            print(e)
            sys.exit('Error creating socket')

    def get_localhost_ip(self):
        '''
        Function: get_localhost_ip - get local IP address with a temporary connection to google.com
        Params: none
        Return: localhost IP address as a string
        '''
        host_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        host_socket.connect(('8.8.8.8', 80))
        localhost_ip = host_socket.getsockname()[0]
        host_socket.close()
        return localhost_ip

    def parse_dig_query(self, packet):
        # TODO implement
        print('parse dig query...')
        # get ip address from dig query

    def run(self):
        '''
        Function: run - runs the DNSServer class by creating a socket connection
                        and continuously parsing incoming dig queries
        Params: none
        Return: none
        '''
        ip_addr = self.get_localhost_ip()
        print(f'IP Address: {ip_addr}')
        try:
            # bind to (ip, port)
            self.udp_socket.bind((ip_addr, int(self.PORT)))
        except Exception as e:
            print(e)
            sys.exit('Error binding socket')

        while True:
            packet = self.udp_socket.recvfrom(self.BUFFER)
            # parse dig query
            self.parse_dig_query(packet)

        # ? close socket - this won't get reached because of infinite loop
        # self.udp_socket.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', action='store', type=int, dest='PORT', help='-p <port>')
    parser.add_argument('-n', action='store', type=str, dest='NAME', help='-n <name>')
    args = parser.parse_args()
    dns_server = DNSServer(args)
    dns_server.run()
