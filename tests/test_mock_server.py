from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder
from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird.mock import context
from lyrebird.task import BackgroundTaskServer
from lyrebird.event import EventServer
from lyrebird import application
from lyrebird import reporter
from typing import NamedTuple
import pytest
from urllib.parse import quote


conf = {
    "version": "0.10.4",
    "proxy.filters": ["kuxun", "meituan", "sankuai", "dianping"],
    "proxy.port": 4272,
    "mock.port": 9090,
    # 'ip': '127.0.0.1',
    "mock.data": "data",
    "mock.proxy_headers": {
        "scheme": "MKScheme",
        "host": "MKOriginHost",
        "port": "MKOriginPort"
    }
}

MockConfigManager = NamedTuple('MockConfigManager', [('config', dict)])


@pytest.fixture
def client():
    # application.config = conf
    application._cm = MockConfigManager(config=conf)
    application.server['event'] = EventServer()
    application.reporter = reporter.Reporter()
    application.server['task'] = BackgroundTaskServer()
    application.encoders_decoders = EncoderDecoder()
    server = LyrebirdMockServer()
    client = server.app.test_client()
    yield client


@pytest.fixture
def clear():
    context.application.cache._cache.clear()


def test_mock_api(client):
    resp = client.get('/mock/http://www.bing.com')
    assert 200 <= resp.status_code <= 400


def test_status_api(client):
    resp = client.get('/api/status')
    assert resp.status_code == 200


def test_mock_api_with_query(client, clear):
    origin_url = 'http://www.bing.com?q=,+%'
    url = quote(origin_url)
    client.get(f'/mock/?url={url}')
    cache_list = context.application.cache
    assert len(cache_list._cache) == 1
    assert cache_list._cache[0]['request']['query']['url'] == url
    assert cache_list._cache[0]['request']['url'] == f'?url={url}'