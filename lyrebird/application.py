from flask import jsonify
from lyrebird.nconfig import ConfigManager

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


_cm: ConfigManager = None

server = {}
plugins = {}


def start_server():
    for name in server:
        server[name].start()


def stop_server():
    for name in server:
        server[name].stop()


class ConfigProxy:

    def get(self, k, default=None):
        return _cm.config.get(k, default)
    
    def __setitem__(self, k, v):
        _cm.config[k] = v

    def __getitem__(self, k):
        return _cm.config[k]


config = ConfigProxy()


def root_dir():
    return _cm.root
