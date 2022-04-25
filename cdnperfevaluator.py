import subprocess, socketserver

import utils

# class PerfEvalHandler(socketserver.BaseRequestHandler):
#     def handle(self) -> None:
#         # Retrieve CDN address and ping to the CDN to retrieve latency information
#         data = self.request.recv(1024)
#         ip_addr, port = self.client_address
#         print(self.request)
#         average_latency = self.http_server_latency(ip_addr)
#         print(average_latency)
        
#         if not average_latency:
#             average_latency = '99999'

#         self.request.send(average_latency)

#     def http_server_latency(self, ip_address: str) -> str:
#         '''
#             Utilize Scamper tool to get the latency statistics by making 1 probe to the CDN servers
#         '''
#         scamper_cmd = "sudo scamper -c 'ping -c 1' -i {}".format(ip_address)
#         scamper_response = subprocess.getoutput(scamper_cmd).splitlines()[-1]

#         if not scamper_response:
#             print('Unable to run Scamper...')
#             return ''
        
#         # Parse Scamper response
#         start_idx = scamper_response.find('=') + 2
#         end_idx = -3
#         minimum, average, maximum, standard_dev = scamper_response[start_idx : end_idx].split('/')
        
#         return average

# class PerformanceEvaluator:
#     def __init__(self, dns_port) -> None:
#         self.port = dns_port

#     def start_measurement(self):
#         server = socketserver.TCPServer((utils.get_my_ip(), self.port), PerfEvalHandler)
#         server.serve_forever()

def http_server_latency(ip_address: str) -> str:
    '''
        Utilize Scamper tool to get the latency statistics by making 1 probe to the CDN servers
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

if __name__ == "__main__":
    # perf_evaluator = PerformanceEvaluator(40008)
    # perf_evaluator.start_measurement()
    print(http_server_latency('50.116.41.109'))