import subprocess, socketserver

import utils

class PerfEvalHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        # Retrieve DNS address and ping to the CDN to retrieve latency information
        ip_addr, port = self.client_address
        print(self.client_address)
        average_latency = self.http_server_latency(ip_addr)
        
        if not average_latency:
            average_latency = '99999'

        self.request.sendall(average_latency)

    def http_server_latency(self, ip_address: str) -> str:
        '''
            Utilize Scamper tool to get the latency statistics by making 1 probe to the CDN server
        '''
        scamper_cmd = "sudo scamper -c 'ping -c 1' -i {}".format(ip_address)
        scamper_response = subprocess.getoutput(scamper_cmd).splitlines()[-1]

        if not scamper_response:
            print('Unable to run Scamper...')
            return ''
        
        # Parse Scamper response
        start_idx = scamper_response.find('=') + 2
        end_idx = -3
        minimum, average, maximum, standard_dev = scamper_response[start_idx : end_idx].split('/')
        
        return average

class PerformanceEvaluator:
    def __init__(self, cdn_ipaddr, cdn_port) -> None:
        self.ip_addr = cdn_ipaddr
        self.port = cdn_port

    def start_measurement(self):
        server = socketserver.TCPServer((self.ip_addr, self.port), PerfEvalHandler)
        server.serve_forever()

if __name__ == "__main__":
    perf_evaluator = PerformanceEvaluator('50.116.41.109', 40008)
    perf_evaluator.start_measurement()
