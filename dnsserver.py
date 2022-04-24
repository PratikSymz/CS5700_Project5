import argparse
import socketserver
from dnslib import *

DEFAULT_SERVER = '50.116.41.109'
BUFFER = 1024

class DigQuery():
    def parse_dig_query(self, data):
        '''
        Function: parse_dig_query - parses incoming dig queries
        Params: packet - tuple of (data, address)
        Return: none
        '''
        # parse dig query
        dig_query = DNSRecord.parse(data)

        question_name = dig_query.q.qname
        question_type = dig_query.q.qtype
        message_id = dig_query.header.id

        # TODO find best replica

        # create response
        response = DNSRecord(
            DNSHeader(id=message_id, qr=1, aa=1, ra=1),
            q=DNSQuestion(dig_query.q.qname, dig_query.q.qtype, dig_query.q.qclass),
            a=RR(
                dig_query.q.qname,
                rdata=A(DEFAULT_SERVER) # TODO replace with ip of replica or origin server
            )
        )
        # if qtype == 1 it is an A record
        # ? do we need to check if str(question_name)[:-1] == hostname ???
        if question_type == 1:
            return response.pack()

class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print(f'client addr: {self.client_address}\n')
        dig_response = DigQuery().parse_dig_query(data)
        print(f'\nresponse: {dig_response}\n\n')
        print('Sending response to client\n')
        socket.sendto(dig_response, self.client_address)


class DNSServer(socketserver.UDPServer):
    def __init__(self, hostname, my_addr, request_handler = RequestHandler):
        # Initialize UDPServer
        socketserver.UDPServer.__init__(self, my_addr, request_handler)

        self.hostname = hostname
        self.buffer = 1024

        # replica servers: key: name, values: 0 - ip, 1 - geolocation lat/lon
        self.replicas = {'p5-http-a.5700.network': ('50.116.41.109', [33.74831,-84.39111]),     # Atlanta, GA
                         'p5-http-b.5700.network': ('45.33.50.187', [37.55148,-121.98330]),     # Fremont, CA
                         'p5-http-c.5700.network': ('194.195.121.150', [-33.86960,151.20691]),  # Sydney, Australia
                         'p5-http-d.5700.network': ('172.104.144.157', [50.11208,8.68341]),     # Frankfurt, Germany
                         'p5-http-e.5700.network': ('172.104.110.211', [35.68408,139.80885]),   # Tokyo, Japan
                         'p5-http-f.5700.network': ('88.80.186.80', [51.50643,-0.12719]),       # London, UK
                         'p5-http-g.5700.network': ('172.105.55.115', [19.14045,72.88235])}     # Mumbai, India

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', action='store', type=int, dest='PORT', help='-p <port>')
    parser.add_argument('-n', action='store', type=str, dest='NAME', help='-n <name>')
    args = parser.parse_args()
    dns_server = DNSServer(args.NAME, ('', args.PORT))
    dns_server.serve_forever()
