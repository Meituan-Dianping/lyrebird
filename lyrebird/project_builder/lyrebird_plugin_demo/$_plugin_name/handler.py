from lyrebird import application
import lyrebird
from lyrebird.application import config
import requests
from flask import request


requestList = []


def on_request(msg):
    uri = msg['flow']['request']['url']
    flow_id = msg['flow']['id']
    item = {
        "uri": uri,
        "id":flow_id
    }
    global requestList
    if len(requestList) > 9:
        requestList.pop()
        requestList.insert(0, item)
    else:
        requestList.insert(0, item)

    lyrebird.emit('loadRequestList')

def mock():
    uri = request.json["uri"]
    ip =  config.get('ip')
    port = config.get('mock.port')

    requests.get(url=f"http://{ip}:{port}/mock/{uri}")
    return application.make_ok_response()

def request_list():
    global requestList
    return application.make_ok_response(
        requestList = requestList
    )

def reset():
    global requestList
    requestList = []
    return application.make_ok_response()
