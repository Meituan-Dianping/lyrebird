from lyrebird import application
import lyrebird
from lyrebird.application import config
import requests
from flask import request


lists = []


def on_request(msg):
    uri = msg['flow']['request']['url']
    id = msg['flow']['id']
    item = {
        "uri": uri,
        "id":id
    }
    global lists
    if len(lists) > 9:
        lists.pop()
        lists.insert(0, item)
    else:
        lists.insert(0, item)

    lyrebird.emit('loadRequestList')

def remock():
    uri = request.json["uri"]
    ip =  config.get('ip')
    port = config.get('mock.port')

    r = requests.get(url=f"http://{ip}:{port}/mock/{uri}")
    return application.make_ok_response()
    

    
def request_list():
    global lists
    return application.make_ok_response(
        requestList = lists
    )


def reset():
    global lists
    lists = []
    return application.make_ok_response()
