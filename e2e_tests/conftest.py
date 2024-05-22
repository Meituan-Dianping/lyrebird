import os
import sys
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
        self.api_long_time_service = f'http://127.0.0.1:{self.port}/long_time_service'

    def start(self):
        self.mock_server_process = subprocess.Popen(
            f'python3 ./e2e_tests/assets/serve.py -port {self.port}', shell=True, start_new_session=True)
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
        self.uri_extra_mock = None
        self._init_port()

    def _init_port(self):
        self.port = self._find_free_port()
        self.proxy_port = self._find_free_port()
        self.extra_mock_port = self._find_free_port()
        self.api_status = f'http://127.0.0.1:{self.port}/api/status'
        self.uri_mock = f'http://127.0.0.1:{self.port}/mock/'
        self.uri_extra_mock = f'http://127.0.0.1:{self.extra_mock_port}/'
        self.api_flows = f'http://127.0.0.1:{self.port}/api/flow'

    def _find_free_port(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def start(self, checker_path=[]):

        cmdline = f'{sys.executable} -m lyrebird -b -v --no-mitm --mock {self.port} --extra-mock {self.extra_mock_port}'
        for path in checker_path:
            cmdline = cmdline + f' --script {path}'
        self.lyrebird_process = subprocess.Popen(cmdline, shell=True, start_new_session=True)
        _wait(requests.get, args=[self.api_status])
        _wait(requests.get, args=[self.uri_extra_mock])

        # Wait for checker to load
        if checker_path:
            time.sleep(3)

    def stop(self):
        if self.lyrebird_process:
            try:
                os.killpg(self.lyrebird_process.pid, signal.SIGINT)
            except PermissionError:
                os.kill(self.lyrebird_process.pid, signal.SIGINT)
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
