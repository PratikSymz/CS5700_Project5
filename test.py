import subprocess

def http_server_latency(ip_address: str):
    '''
        Utilize Scamper tool to get the latency statistics by making 1 probe to the CDN server
    '''
    scamper_cmd = "sudo scamper -c 'ping -c 1' -i {}".format(ip_address)
    scamper_response = subprocess.getoutput(scamper_cmd)

    if not scamper_response:
        print('Unable to run Scamper...')
        return ''
    
    # Parse Scamper response
    # start_idx = scamper_response.find('=') + 2
    # end_idx = -3
    # minimum, average, maximum, standard_dev = scamper_response[start_idx : end_idx].split('/')
    # return average, float(average)
    return scamper_response


if __name__ == "__main__":
    print(http_server_latency('172.105.55.115'))