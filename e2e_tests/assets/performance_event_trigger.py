from lyrebird import on_request, on_request_upstream
from lyrebird import on_response, on_response_upstream
from lyrebird import application

@on_response()
def on_response_publish(flow):
    application.server['event'].publish('test', {'data' : ''})
