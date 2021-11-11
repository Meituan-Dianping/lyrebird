from lyrebird.mock import headers

def kill_flow(flow):
    request_headers = flow['request']['headers']
    if not request_headers.get(headers.MITMPROXY_CLIENT_ADDRESS):
        return
    flow['request']['headers'][headers.MITMPROXY_COMMAND] = 'kill'

    flow['response']['code'] = 0
    flow['response']['headers'] = {}
    flow['response']['data'] = ''
