from lyrebird.mock import headers

def kill(flow):
    request_headers = flow['request']['headers']
    if not request_headers.get(headers.mitmproxy_client_address):
        return
    flow['request']['headers'][headers.mitmproxy_command] = 'kill'

    flow['response']['code'] = 0
    flow['response']['headers'] = {}
    flow['response']['data'] = ''
