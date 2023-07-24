import pytest
from lyrebird import application
from lyrebird.mock import context
from lyrebird.config import ConfigManager
from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder

def get_server():
    application._cm = ConfigManager()
    application._cm.config = _conf
    application.encoders_decoders = EncoderDecoder()
    server = LyrebirdMockServer()
    server.app.testing = True
    return server

_conf = {
    'ip': '127.0.0.1',
    'mock.port': 9090
}

test_word_encode = r'%E4%BD%A0%E5%A5%BD%EF%BC%8C%E4%B8%96%E7%95%8C'
test_word_decode = '你好，世界'

with get_server().app.test_client() as init_client:
    context.application.cache._cache.clear()
    init_client.get('/mock/http://i.meituan.com')
    init_client.get('/mock/http://www.bing.com')
    init_client.get('/mock/http://www.baidu.com')
    init_client.get(f'/mock/http://m.meituan.com?word={test_word_encode}')
    init_client.get(f'/mock/http://g.meituan.com?word={test_word_decode}')

@pytest.fixture
def client():
    server = get_server()
    client = server.app.test_client()
    ctx = server.app.app_context()
    yield client


def test_flow_list_with_get(client):
    resp = client.get('/api/flow')
    assert len(resp.json) == 5


def test_flow_list_with_post_and_search_simple(client):
    resp = client.post('/api/flow/search', json={'selectedFilter': {
                                                    'ignore': [
                                                        'www.bing.com',
                                                        'www.baidu.com',
                                                        'm.meituan.com',
                                                        'g.meituan.com'
                                                    ]
                                                }})
    assert len(resp.json) == 1 and resp.json[0]['request']['host'] == 'i.meituan.com'


def test_flow_list_with_post_and_search_advanced_must(client):
    resp = client.post('/api/flow/search', json={'selectedFilter': {
                                                    'advanced': {
                                                        'must': {
                                                            'request.url': [
                                                                'www.bing.com'
                                                            ]
                                                        }
                                                    }
                                                }})
    assert len(resp.json) == 1 and resp.json[0]['request']['host'] == 'www.bing.com'


def test_flow_list_with_post_and_search_advanced_must_not(client):
    resp = client.post('/api/flow/search', json={'selectedFilter': {
                                                    'advanced': {
                                                        'must_not': {
                                                            'request.url': [
                                                                'www.baidu.com',
                                                                'www.bing.com',
                                                                'm.meituan.com',
                                                                'g.meituan.com'
                                                            ]
                                                        }
                                                    }
                                                }})
    assert len(resp.json) == 1 and resp.json[0]['request']['host'] == 'i.meituan.com'


def test_flow_list_with_post_and_search_both_advanced_condition(client):
    resp = client.post('/api/flow/search', json={'selectedFilter': {
                                                    'advanced': {
                                                        'must_not': {
                                                            'request.url': [
                                                                'www.baidu.com',
                                                                'm.meituan.com',
                                                                'g.meituan.com'
                                                            ]
                                                        },
                                                        'must': {
                                                            'request.url': [
                                                                'i.meituan.com'
                                                            ]
                                                        }
                                                    }
                                                }})
    assert len(resp.json) == 1 and resp.json[0]['request']['host'] == 'i.meituan.com'


def test_flow_with_id(client):
    flow_id = client.post('/api/flow/search', json={'selectedFilter':''}).json[0]['id']
    resp = client.get(f'/api/flow/{flow_id}')
    assert resp.json['code'] == 1000


def test_flow_with_id_and_decode_input_encode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_decode=true')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == test_word_decode


def test_flow_with_id_and_decode_input_decode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'g.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_decode=true')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == test_word_decode


def test_flow_with_id_and_decode_use_capital_letter_true(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_decode=True')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == test_word_decode


def test_flow_with_id_and_decode_use_capital_letter_false(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_decode=FALSE')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == test_word_encode


def test_flow_with_id_and_no_decode_input_encode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == test_word_encode


def test_flow_with_id_and_no_decode_input_decode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'g.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == test_word_decode
