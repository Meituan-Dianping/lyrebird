from lyrebird import on_request

@on_request(rules={
    "request.url": "(?=.*poi/detail)"
})
def add_request_param(flow):
    if '?' in flow['request']['url']:
        flow['request']['url'] += '&param=1'
    else:
        flow['request']['url'] += '?param=1'
