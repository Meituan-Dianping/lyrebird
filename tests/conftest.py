import pytest
from lyrebird import application
from lyrebird.mock import context
from lyrebird.application import SyncManager

SERVER_NAMES = ['event', 'log', 'mock', 'task', 'checker', 'db', 'plugin']

@pytest.fixture(scope='module', autouse=True)
def setup_and_teardown_environment():
    bak_server = {}
    for server in SERVER_NAMES:
        bak_server[server] = application.server.get(server)
    bak_reporter = application.reporter
    bak_cm = application._cm
    bak_config = application.config
    bak_encoder_decoder = application.encoders_decoders
    bak_on_request = application.on_request
    bak_on_request_upstream = application.on_request_upstream
    bak_on_response = application.on_response
    bak_on_response_upstream = application.on_response_upstream
    bak_socketio = context.application.socket_io
    bak_dm = context.application.data_manager

    yield

    for server in SERVER_NAMES:
        if bak_server[server] is None and server in application.server:
            del application.server[server]
        elif bak_server[server] is not None:
            application.server[server] = bak_server[server]
    application.reporter = bak_reporter
    application._cm = bak_cm
    application.config = bak_config
    application.encoders_decoders = bak_encoder_decoder
    application.on_request = bak_on_request
    application.on_request_upstream = bak_on_request_upstream
    application.on_response = bak_on_response
    application.on_response_upstream = bak_on_response_upstream
    context.application.socket_io = bak_socketio
    context.application.data_manager = bak_dm


@pytest.fixture(scope='function', autouse=True)
def init_sync_manager():
    application.sync_manager = SyncManager()
    yield
    application.sync_manager.broadcast_to_queues(None)
    application.sync_manager.destory()
    application.sync_manager = None
