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


def make_fail_response(msg, **kwargs):
    fail_resp = {
        "code": 3000,
        "message": msg
    }
    fail_resp.update(kwargs)
    return jsonify(fail_resp)


# Lyrebird status contains: 'READY' and 'INITING'
status = 'INITING'

_cm = None
_src = None


server = {}
plugins = {}
active_menu = {}


notice = None
checkers = {}

on_request = []
on_response = []
on_request_upstream = []
on_response_upstream = []

encoder = []
decoder = []

labels = None

encoders_decoders = None

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

    def raw(self):
        return _cm.config


config = ConfigProxy()

# statistics reporter
reporter = None


def root_dir():
    if _cm:
        return _cm.ROOT
