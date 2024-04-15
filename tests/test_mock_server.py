from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder
from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird.mock import context
from lyrebird import application
from .utils import FakeEvnetServer, FakeReportor, FakeBackgroundTaskServer

import json
import pytest
import binascii
from typing import NamedTuple
from urllib.parse import quote, urlencode


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
    application._cm = MockConfigManager(config=conf)
    application.server['event'] = FakeEvnetServer()
    application.reporter = FakeReportor()
    application.server['task'] = FakeBackgroundTaskServer()
    application.encoders_decoders = EncoderDecoder()
    server = LyrebirdMockServer()
    server.app.testing = True
    with server.app.test_client() as client:
        yield client
    server.terminate()


@pytest.fixture
def clear():
    context.application.cache._cache.clear()


@pytest.fixture
def keep_origin_data():
    application.config['mock.request.keep_origin_data'] = True


def test_mock_api(client):
    resp = client.get('/mock/http://www.bing.com')
    assert 200 <= resp.status_code <= 400


def test_status_api(client):
    resp = client.get('/api/status')
    assert resp.status_code == 200


def test_mock_api_with_query(client, clear):
    origin_url = 'http://www.bing.com?q=,+%'
    url = quote(origin_url, safe='')
    client.get(f'/mock/?url={url}')
    cache_list = context.application.cache
    assert len(cache_list._cache) == 1
    assert cache_list._cache[0]['request']['query']['url'] == url
    assert cache_list._cache[0]['request']['url'] == f'?url={url}'


def test_mock_api_put(client, clear):
    url = '/mock/http://www.bing.com'
    origin_json = {
        'name': 'Lyrebird'
    }
    origin_body = json.dumps(origin_json)
    headers = {'Content-Type': 'application/json'}

    client.put(url, headers=headers, data=origin_body)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['request']['data']
    assert origin_json == flow_body


def test_mock_api_patch(client, clear):
    url = '/mock/http://www.bing.com'
    origin_json = {
        'name': 'Lyrebird'
    }
    origin_body = json.dumps(origin_json)
    headers = {'Content-Type': 'application/json'}

    client.patch(url, headers=headers, data=origin_body)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['request']['data']
    assert origin_json == flow_body


def test_mock_content_type_json(client, clear):
    url = '/mock/http://www.bing.com'
    origin_json = {
        'name': 'Lyrebird'
    }
    origin_body = json.dumps(origin_json)
    headers = {'Content-Type': 'application/json'}

    client.post(url, headers=headers, data=origin_body)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['request']['data']

    assert origin_json == flow_body


def test_mock_content_type_javascript(client, clear):
    url = '/mock/http://www.bing.com'
    origin_js = 'console.log("Hello, world!");'
    headers = {'Content-Type': 'application/javascript'}

    client.post(url, headers=headers, data=origin_js)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['request']['data']

    assert origin_js == flow_body


def test_mock_content_type_text(client, clear):
    url = '/mock/http://www.bing.com'
    origin_text = 'Hello, world!'
    headers = {'Content-Type': 'text/plain'}

    client.post(url, headers=headers, data=origin_text)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['request']['data']

    assert origin_text == flow_body


def test_mock_content_type_form(client, clear):
    url = '/mock/http://www.bing.com'
    origin_data = 'name=Lyrebird&com=mt&blank='
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    client.post(url, headers=headers, data=origin_data)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['request']['data']

    assert origin_data == urlencode(flow_body)


def test_mock_content_type_default(client, clear):
    url = '/mock/http://www.bing.com'
    origin_data = b'Lyrebird'
    headers = {'Content-Type': 'image/png'}

    client.post(url, headers=headers, data=origin_data)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['request']['data']

    flow_body_a2b = binascii.a2b_base64(flow_body.encode())

    assert origin_data == flow_body_a2b


def test_mock_content_type_json_keep_origin_request(client, clear, keep_origin_data):
    url = '/mock/http://www.bing.com'
    origin_json = {
        'name': 'Lyrebird'
    }
    origin_body = json.dumps(origin_json)
    headers = {'Content-Type': 'application/json'}

    client.post(url, headers=headers, data=origin_body)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['origin_request']['data']

    assert origin_body == flow_body


def test_mock_content_type_javascript_keep_origin_request(client, clear, keep_origin_data):
    url = '/mock/http://www.bing.com'
    origin_js = 'console.log("Hello, world!");'
    headers = {'Content-Type': 'application/javascript'}

    client.post(url, headers=headers, data=origin_js)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['origin_request']['data']

    assert origin_js == flow_body


def test_mock_content_type_text_keep_origin_request(client, clear, keep_origin_data):
    url = '/mock/http://www.bing.com'
    origin_text = 'Hello, world!'
    headers = {'Content-Type': 'text/plain'}

    client.post(url, headers=headers, data=origin_text)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['origin_request']['data']

    assert origin_text == flow_body


def test_mock_content_type_form_keep_origin_request(client, clear, keep_origin_data):
    url = '/mock/http://www.bing.com'
    origin_data = 'name=Lyrebird&com=mt&blank'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    client.post(url, headers=headers, data=origin_data)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['origin_request']['data']

    assert origin_data == flow_body


def test_mock_content_type_default_keep_origin_request(client, clear, keep_origin_data):
    url = '/mock/http://www.bing.com'
    origin_data = b'Lyrebird'
    headers = {'Content-Type': 'image/png'}

    client.post(url, headers=headers, data=origin_data)

    cache_list = context.application.cache
    assert len(cache_list._cache) == 1

    flow = cache_list._cache[0]
    flow_body = flow['origin_request']['data']

    flow_body_a2b = binascii.a2b_base64(flow_body.encode())

    assert origin_data == flow_body_a2b
