import argparse
import utils
import socketserver
from dnslib import *
import maxminddb
import math


DEFAULT_SERVER = ('p5-http-a.5700.network', '50.116.41.109')
BUFFER = 1024

replicas = {'p5-http-a.5700.network': socket.gethostbyname('p5-http-a.5700.network'),
                'p5-http-b.5700.network': socket.gethostbyname('p5-http-b.5700.network'),
                'p5-http-c.5700.network': socket.gethostbyname('p5-http-c.5700.network'),
                'p5-http-d.5700.network': socket.gethostbyname('p5-http-d.5700.network'),
                'p5-http-e.5700.network': socket.gethostbyname('p5-http-e.5700.network'),
                'p5-http-f.5700.network': socket.gethostbyname('p5-http-f.5700.network'),
                'p5-http-g.5700.network': socket.gethostbyname('p5-http-g.5700.network')}

class GeoIP:
    def __init__(self):
        self.reader = maxminddb.open_database('GeoLite2-City.mmdb')

    def get_location(self, ip):
        response = self.reader.get(ip)
        # print(f'city: {response["city"]["names"]["en"]}')
        latitude, longitude = response['location']['latitude'], response['location']['longitude']
        return latitude, longitude

class RequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print(f'client addr: {self.client_address}\n')
        dig_response = self.parse_dig_query(data)
        print('Sending response to client\n')
        socket.sendto(dig_response, self.client_address)

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

        # get nearest replica
        nearest_replica = self.find_nearest_replica(self.client_address[0])

        # create response
        response = DNSRecord(
            DNSHeader(id=message_id, qr=1, aa=1, ra=1),
            q=DNSQuestion(dig_query.q.qname, dig_query.q.qtype, dig_query.q.qclass),
            a=RR(
                nearest_replica,
                rdata=A(replicas[nearest_replica])
            )
        )
        # if qtype == 1 it is an A record
        # ? do we need to check if str(question_name)[:-1] == hostname ???
        if question_type == 1:
            return response.pack()

    def get_nearest_replica(self, client_addr):
        geo_ip = GeoIP()
        client_lat, client_lon = geo_ip.get_location('194.195.121.150') # TODO change back to self.client_address[0]
        nearest_replica = ''
        min_distance = float('inf')
        for replica in replicas.keys():
            lat, lon = geo_ip.get_location(replicas[replica])
            print(f'replica location: {lat}, {lon}')
            # get distance between client and replica
            distance = self.get_distance(lat, lon, client_lat, client_lon)
            # print(f'Distance between replica {replica} and client: {distance}\n')
            if distance < min_distance:
                min_distance = distance
                nearest_replica = replica
        # print(f'Nearest replica: {nearest_replica}')
        return nearest_replica

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
