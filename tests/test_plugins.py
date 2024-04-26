import pytest
from .utils import FakeEvnetServer, FakeBackgroundTaskServer
from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird import application
from lyrebird.plugins import PluginManager
from lyrebird.config import ConfigManager
import copy

CONTENT_MANIFEST_A = u'''
from lyrebird.plugins import manifest
from . import handler
manifest(
    id='demo',
    name='demo',
    icon='mdi-wan',
    api=[],
    on_request=[
        ('test', handler.func, None, 1)
    ],
    on_response=[
        ('test', handler.func, None, 1)
    ],
    on_request_upstream=[
        ('test', handler.func, None, 1)
    ],
    on_response_upstream=[
        ('test', handler.func, None, 1)
    ],
    status=[]
)'''
CONTENT_MANIFEST_B = u'''
from lyrebird.plugins import manifest
from . import handler
manifest(
    id='demo',
    name='demo',
    icon='mdi-wan',
    api=[],
    on_request=[
        ('test', handler.func, None, 's')
    ],
    on_response=[
        ('test', handler.func, None, 's')
    ],
    on_request_upstream=[
        ('test', handler.func, None, 's')
    ],
    on_response_upstream=[
        ('test', handler.func, None, 's')
    ],
    status=[]
)'''
CONTENT_HANDLER = u"def func():\n\tpass"
CONTENT_MANIFEST_IN = u"graft lyrebird_demo\nrecursive-exclude * *.pyc *.pyo *.swo *.swp *.map *.DS_Store"
CONTENT_INIT_FILE = u""
CONTENT_VERSION = u'IVERSION = (0, 1, 0)\nVERSION = ".".join(str(i) for i in IVERSION)'
CONTEST_SETUP_FILE = u'''
from setuptools import setup, find_packages
import runpy
import os

here = os.path.abspath(os.path.dirname(__file__))

VERSION = runpy.run_path(
    os.path.join(here, 'lyrebird_demo', 'version.py')
)['VERSION']

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='demo',
    version=VERSION,
    packages=find_packages(),
    url='',
    author='',
    author_email='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        'lyrebird_plugin': [
            'lyrebird_demo = lyrebird_demo.manifest'
        ]
    },
    install_requires=[
        'lyrebird'
    ]
)'''

conf = {
    'version': '0.10.4',
    'proxy.filters': ['kuxun', 'meituan', 'sankuai', 'dianping'],
    'proxy.port': 4272,
    'mock.port': 9090,
    'ip': '127.0.0.1',
    'mock.data': 'data',
    'mock.proxy_headers': {
        'scheme': 'MKScheme',
        'host': 'MKOriginHost',
        'port': 'MKOriginPort'
    }
}


@pytest.fixture
def mock_server():
    application._cm = ConfigManager()
    application._cm.config = copy.deepcopy(conf)
    server = LyrebirdMockServer()
    application.server['task'] = FakeBackgroundTaskServer()
    application.server['mock'] = server
    yield server
    server.terminate()
    del server


@pytest.fixture
def event_server():
    application.server['event'] = FakeEvnetServer()


@pytest.fixture
def plugin_init_plugin_A(tmp_path):

    setup_file = tmp_path / 'setup.py'
    setup_file.write_text(CONTEST_SETUP_FILE)
    manifest_in = tmp_path / 'MANIFEST.in'
    manifest_in.write_text(CONTENT_MANIFEST_IN)

    lyrebird_demo = tmp_path / 'lyrebird_demo'
    lyrebird_demo.mkdir()
    manifest = lyrebird_demo / 'manifest.py'
    manifest.write_text(CONTENT_MANIFEST_A)
    handler_file = lyrebird_demo / 'handler.py'
    handler_file.write_text(CONTENT_HANDLER)
    init_file = lyrebird_demo / '__init__.py'
    init_file.write_text(CONTENT_INIT_FILE)
    version = lyrebird_demo / 'version.py'
    version.write_text(CONTENT_VERSION)

    return tmp_path

@pytest.fixture
def plugin_init_plugin_B(tmp_path):

    setup_file = tmp_path / 'setup.py'
    setup_file.write_text(CONTEST_SETUP_FILE)
    manifest_in = tmp_path / 'MANIFEST.in'
    manifest_in.write_text(CONTENT_MANIFEST_IN)

    lyrebird_demo = tmp_path / 'lyrebird_demo'
    lyrebird_demo.mkdir()
    manifest = lyrebird_demo / 'manifest.py'
    manifest.write_text(CONTENT_MANIFEST_B)
    handler_file = lyrebird_demo / 'handler.py'
    handler_file.write_text(CONTENT_HANDLER)
    init_file = lyrebird_demo / '__init__.py'
    init_file.write_text(CONTENT_INIT_FILE)
    version = lyrebird_demo / 'version.py'
    version.write_text(CONTENT_VERSION)

    return tmp_path


@pytest.fixture
def plugin_server_A(plugin_init_plugin_A):
    server = PluginManager()
    server.start()
    server.plugin_path_list = [plugin_init_plugin_A]
    server.reload()
    application.server['plugin'] = server
    yield server
    server.stop()


@pytest.fixture
def plugin_server_B(plugin_init_plugin_B):
    server = PluginManager()
    server.start()
    server.plugin_path_list = [plugin_init_plugin_B]
    server.reload()
    application.server['plugin'] = server
    yield server
    server.stop()

@pytest.fixture
def clear():
    application.on_request = []
    application.on_response = []
    application.on_request_upstream = []
    application.on_response_upstream = []


def test_load_plugin_rank_valid(event_server, mock_server, plugin_server_A):
    assert application.on_request[0]['rank'] == 1
    assert application.on_response[0]['rank'] == 1
    assert application.on_request_upstream[0]['rank'] == 1
    assert application.on_response_upstream[0]['rank'] == 1


def test_load_plugin_rank_invalid(event_server, mock_server, clear, plugin_server_B):
    assert application.on_request[0]['rank'] == 0
    assert application.on_response[0]['rank'] == 0
    assert application.on_request_upstream[0]['rank'] == 0
    assert application.on_response_upstream[0]['rank'] == 0

