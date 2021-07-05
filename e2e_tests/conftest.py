import os
import signal
import pytest
import time
import subprocess
import requests
import socket
from contextlib import closing


def _wait(func, args=[], kwargs={}, timeout=15):
    count = 0
    while True:
        try:
            func(*args, **kwargs)
            return
        except Exception:
            count += 1
            time.sleep(1)
        if count > timeout:
            raise TimeoutError

def _wait_exception(func, args=[], kwargs={}, timeout=15):
    count = 0
    while True:
        try:
            func(*args, **kwargs)
            count += 1
            time.sleep(1)
        except Exception:
            return
        if count > timeout:
            raise TimeoutError

class MockServer:
    def __init__(self):
        self.mock_server_process = None
        self.port = None
        self.api_status = None
        self.api_post = None
        self._init_port()

    def _init_port(self):
        self.port = 5000
        self.api_status = f'http://127.0.0.1:{self.port}/status'
        self.api_post = f'http://127.0.0.1:{self.port}/e2e_serve'

    def start(self):
        self.mock_server_process = subprocess.Popen(f'python3 ./assets/serve.py -port {self.port}', shell=True, start_new_session=True)
        _wait(requests.get, args=[self.api_status])

    def stop(self):
        if self.mock_server_process:
            os.killpg(self.mock_server_process.pid, signal.SIGTERM)
            _wait_exception(requests.get, args=[self.api_status])
            self.mock_server_process = None

class Lyrebird:

    def __init__(self):
        self.lyrebird_process = None
        self.port = None
        self.proxy_port = None
        self.extra_mock_port = None
        self.api_status = None
        self.uri_mock = None
        self._init_port()

    def _init_port(self):
        self.port = 9090
        self.proxy_port = 4272
        self.extra_mock_port = 9999
        self.api_status = f'http://127.0.0.1:{self.port}/api/status'
        self.uri_mock = f'http://127.0.0.1:{self.port}/mock/'

    def start(self, checker_path=None):
        cmdline = f'lyrebird -b -v --mock {self.port} --proxy {self.proxy_port} --extra-mock {self.extra_mock_port}'
        if checker_path:
            cmdline = cmdline + f' --script {checker_path}'
        self.lyrebird_process = subprocess.Popen(cmdline, shell=True, start_new_session=True)
        _wait(requests.get, args=[self.api_status])

        # Wait for checker to load
        if checker_path:
            time.sleep(3)

    def stop(self):
        if self.lyrebird_process:
            os.killpg(self.lyrebird_process.pid, signal.SIGTERM)
            _wait_exception(requests.get, args=[self.api_status])
            self.lyrebird_process = None
            

@pytest.fixture
def lyrebird(request):
    lb = Lyrebird()
    def stop_server():
        lb.stop()
    request.addfinalizer(stop_server)
    lb.start()
    return lb


@pytest.fixture
def lyrebird_with_args(request):
    lb = Lyrebird()
    def stop_server():
        lb.stop()
    request.addfinalizer(stop_server)
    return lb


@pytest.fixture
def mock_server(request):
    mserver = MockServer()
    mserver.start()
    def stop_server():
        mserver.stop()
    request.addfinalizer(stop_server)
    return mserver
