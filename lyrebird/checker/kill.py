from lyrebird.mock import headers

def kill_flow(flow):
    request_headers = flow['request']['headers']
    if not request_headers.get(headers.MITMPROXY_CLIENT_ADDRESS):
        return

    flow['response']['code'] = 0
    flow['response']['headers'] = {}
    flow['response']['data'] = ''

    flow['response']['headers'][headers.MITMPROXY_COMMAND] = 'kill'
