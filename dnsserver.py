import argparse
import socketserver
from dnslib import *

DEFAULT_SERVER = ('p5-http-a.5700.network', '50.116.41.109')
BUFFER = 1024

class DigQuery():
    def parse_dig_query(self, data):
        '''
        Function: parse_dig_query - parses incoming dig queries
        Params: packet - tuple of (data, address)
        Return: none
        '''
        """ Reference: www.zytrax.com/books/dns/ch15/ """
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
                DEFAULT_SERVER[0],
                rdata=A(DEFAULT_SERVER[1]) # TODO replace with ip of replica or origin server
            )
        )
        # if qtype == 1 it is an A record
        # ? do we need to check if str(question_name)[:-1] == hostname ???
        if question_type == 1:
            return response.pack()

    def get_distance(self, lat1, lon1, lat2, lon2):
        '''
        Function: get_distance - calculates distance between two points
        Params: lat1, lon1, lat2, lon2 - floats
        Return: distance - float
        '''
        # convert to radians
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371

        return c * r

class DNSServer(socketserver.UDPServer):
    def __init__(self, hostname, my_addr, request_handler = RequestHandler):
        # Initialize UDPServer
        socketserver.UDPServer.__init__(self, my_addr, request_handler)
        print(f'server address: {self.server_address}')

        self.hostname = hostname
        self.buffer = 1024

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', action='store', default=40008, type=int, dest='PORT', help='-p <port>')
    parser.add_argument('-n', action='store', type=str, dest='NAME', help='-n <name>')
    args = parser.parse_args()
    dns_server = DNSServer(args.NAME, (utils.get_my_ip(), args.PORT))
    dns_server.serve_forever()
