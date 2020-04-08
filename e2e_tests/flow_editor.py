from lyrebird import on_request, on_request_upstream
from lyrebird import on_response, on_response_upstream

@on_request()
def on_request001(flow):
    print(flow['request']['url'])

@on_request_upstream()
def on_request_upstream001(flow):
    print(flow['request']['url'])

@on_response()
def on_response001(flow):
    print(flow['request']['url'])

@on_response_upstream()
def on_response_upstream001(flow):
    print(flow['request']['url'])
