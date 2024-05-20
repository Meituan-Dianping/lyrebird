import webbrowser

import multiprocessing
from queue import Queue
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


def start_server_without_mock_and_log():
    for name in server:
        if name == 'mock' or name == 'log':
            continue
        server[name].start()


def start_mock_server():
    server['mock'].start()


def start_log_server():
    server['log'].start()


def start_server():
    for name in server:
        server[name].start()


def stop_server():
    for name in server:
        server[name].stop()
    sync_manager.broadcast_to_queues(None)

def terminate_server():
    for name in server:
        server[name].terminate()


class SyncManager():
    def __init__(self) -> None:
        global sync_namespace
        self.manager = multiprocessing.Manager()
        self.async_objs = {
            'manager_queues': [],
            'multiprocessing_queues': [],
            'namespace': [],
            'locks': []
        }
        sync_namespace = self.get_namespace()
    
    def get_namespace(self):
        namespace = self.manager.Namespace()
        self.async_objs['namespace'].append(namespace)
        return namespace

    def get_queue(self):
        queue = self.manager.Queue()
        self.async_objs['manager_queues'].append(queue)
        return queue

    def get_thread_queue(self):
        queue = Queue()
        return queue

    def get_multiprocessing_queue(self):
        queue = multiprocessing.Queue()
        self.async_objs['multiprocessing_queues'].append(queue)
        return queue

    def get_lock(self):
        lock = multiprocessing.Lock()
        self.async_objs['locks'].append(lock)
        return lock
    
    def broadcast_to_queues(self, msg):
        for q in self.async_objs['multiprocessing_queues']:
            q.put(msg)
        for q in self.async_objs['manager_queues']:
            q.put(msg)

    def destory(self):
        for q in self.async_objs['multiprocessing_queues']:
            q.close()
            del q
        for q in self.async_objs['manager_queues']:
            q._close()
            del q
        for ns in self.async_objs['namespace']:
            del ns
        for lock in self.async_objs['locks']:
            del lock
        self.manager.shutdown()
        self.manager.join()
        self.manager = None
        self.async_objs = None


sync_manager = {}
sync_namespace = {}


class ConfigProxy:

    def get(self, k, default=None):
        return _cm.config.get(k, default)

    def __setitem__(self, k, v):
        _cm.config[k] = v

    def __getitem__(self, k):
        return _cm.config[k]

    def raw(self):
        if hasattr(_cm.config, 'raw'):
            return _cm.config.raw()
        else:
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
    else:
        status_checkpoints[module] = False

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
    server['event'].subscribe({
        'name': 'status_listener',
        'channel': 'system',
        'func': status_listener
    })


def status_ready():
    server['event'].publish('system', {
        'system': {'action': 'init_module', 'status': 'READY', 'module': 'main'}
    })
