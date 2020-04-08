from lyrebird import on_request, on_request_upstream
from lyrebird import on_response, on_response_upstream

@on_request()
def on_request(flow):
    print(flow['request']['url'])

@on_request_upstream()
def on_request_upstream(flow):
    print(flow['request']['url'])

@on_response()
def on_response(flow):
    print(flow['request']['url'])

@on_response_upstream()
def on_response_upstream(flow):
    print(flow['request']['url'])
