import webbrowser

from flask import jsonify
from functools import reduce

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


def start_server_without_mock():
    for name in server:
        if name == 'mock':
            continue
        server[name].start()


def start_mock_server():
    server['mock'].start()


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


NO_BROSWER = False

# --------- Lyrebird status ---------
'''
[INITING] --> /run lyrebird main method/  --> [READY]
              /start services          / 
              /extra mock server ready /
              /mitm proxy server ready /
'''

# Lyrebird status contains: 'READY' and 'INITING'
status = 'INITING'

# mitm proxy check point will be added if args set useing mitm server (--no-mitm False)
status_checkpoints = {
    'main': False,
    'extra_mock': False
}


def status_listener(event):
    '''
    event example
    event = {
        'channel': 'system',
        'system': {
            'action': 'init_module',
            'status': 'READY',
            'module': 'main'
        }
    }
    '''

    system = event.get('system')
    if not system:
        return

    action = system.get('action')
    if action != 'init_module':
        return

    module = system.get('module')
    if module not in status_checkpoints:
        return

    module_status = system.get('status')
    if module_status == 'READY':
        status_checkpoints[module] = True

    is_all_status_checkpoints_ok = reduce(lambda x, y: x and y, status_checkpoints.values())
    if is_all_status_checkpoints_ok:
        # Set global status
        global status
        status = 'READY'

        server['event'].publish('system', {'action': 'init_module', 'status': 'READY', 'module': 'all'})

        # auto open web browser
        if not NO_BROSWER:
            webbrowser.open(f'http://localhost:{config["mock.port"]}')

def process_status_listener():
    server['event'].subscribe('system', status_listener)


def status_ready():
    server['event'].publish('system', {
        'system': {'action': 'init_module', 'status': 'READY', 'module': 'main'}
    })
