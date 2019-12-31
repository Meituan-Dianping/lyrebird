from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird.task import BackgroundTaskServer
from lyrebird.event import EventServer
from lyrebird import application
from lyrebird import reporter
import pytest


conf = {
    "version": "0.10.4",
    "proxy.filters": ["kuxun", "meituan", "sankuai", "dianping"],
    "proxy.port": 4272,
    "mock.port": 9090,
    "mock.data": "data",
    "mock.proxy_headers": {
        "scheme": "MKScheme",
        "host": "MKOriginHost",
        "port": "MKOriginPort"
    }
}


@pytest.fixture
def client():
    application.config = conf
    application.server['event'] = EventServer()
    application.reporter = reporter.Reporter()
    application.server['task'] = BackgroundTaskServer()
    server = LyrebirdMockServer()
    client = server.app.test_client()
    yield client


def test_mock_api(client):
    resp = client.get('/mock/http://www.google.com')
    assert resp.status_code == 200


def test_status_api(client):
    resp = client.get('/api/status')
    assert resp.status_code == 200
