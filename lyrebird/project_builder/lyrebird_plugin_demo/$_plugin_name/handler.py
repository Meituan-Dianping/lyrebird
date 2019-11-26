from flask import jsonify
from lyrebird import application

req_count = 0
last_req_url = None


def on_request(msg):
    global req_count
    req_count += 1
    global last_req_url
    last_req_url = msg['flow']['request']['url']


def request_count():
    return application.make_ok_response(
        count=req_count,
        last_request=last_req_url
    )


def reset_count():
    global req_count
    req_count = 0
    global last_req_url
    last_req_url = None
    return application.make_ok_response()
