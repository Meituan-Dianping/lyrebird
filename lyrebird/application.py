from flask import jsonify

"""
Lyrebird context

"""

def make_ok_response(**kwargs):
    ok_resp = {
            "code": 1000,
            "message": "success"
        }
    ok_resp.update(kwargs)
    return jsonify(ok_resp)


def make_fail_response(msg):
    return jsonify(
        {
            "code": 3000,
            "message": msg
        }
    )


config = {}
server = {}
plugins = {}


def start_server():
    for name in server:
        server[name].start()
