import pytest
from lyrebird import application
from lyrebird.mock import context
from lyrebird.config import ConfigManager
from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder

TEST_WORD_ENCODE = r'%E4%BD%A0%E5%A5%BD%EF%BC%8C%E4%B8%96%E7%95%8C'
TEST_WORD_DECODE = '你好，世界'

REQUEST_URL = [
    '/mock/http://www.meituan.com',
    '/mock/http://www.bing.com',
    '/mock/http://www.dianping.com',
    f'/mock/http://m.meituan.com?word={TEST_WORD_ENCODE}',
    f'/mock/http://i.meituan.com?word={TEST_WORD_DECODE}'
]

TEST_FILTER = [
    {
        'name': 'test_search_simple',
        'desc': '',
        'ignore': [
            'www.bing.com',
            'www.dianping.com',
            'm.meituan.com',
            'i.meituan.com'
        ]
    },
    {
        'name': 'test_search_advanced_must',
        'desc': '',
        'advanced': {
            'must': {
                'request.url': [
                    'www.bing.com'
                ]
            }
        }
    },
    {
        'name': 'test_search_advanced_must_not',
        'desc': '',
        'advanced': {
            'must_not': {
                'request.url': [
                    'www.dianping.com',
                    'www.bing.com',
                    'm.meituan.com',
                    'i.meituan.com'
                ]
            }
        }
    },
    {
        'name': 'test_search_both_advanced_condition',
        'desc': '',
        'advanced': {
            'must_not': {
                'request.url': [
                    'www.dianping.com',
                    'm.meituan.com',
                    'i.meituan.com'
                ]
            },
            'must': {
                'request.url': [
                    'www.meituan.com'
                ]
            }
        }
    }
]

_conf = {
    'ip': '127.0.0.1',
    'mock.port': 9090,
    'inspector.filters': TEST_FILTER
}

def get_server():
    application._cm = ConfigManager()
    application._cm.config = _conf
    application.encoders_decoders = EncoderDecoder()
    server = LyrebirdMockServer()
    server.app.testing = True
    return server



with get_server().app.test_client() as init_client:
    context.application.cache._cache.clear()
    for url in REQUEST_URL:
        init_client.get(url)

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
    resp = client.post('/api/flow/search', json={'selectedFilter': 'test_search_simple'})
    assert len(resp.json) == 1 and resp.json[0]['request']['host'] == 'www.meituan.com'


def test_flow_list_with_post_and_search_advanced_must(client):
    resp = client.post('/api/flow/search', json={'selectedFilter': 'test_search_advanced_must'})
    assert len(resp.json) == 1 and resp.json[0]['request']['host'] == 'www.bing.com'


def test_flow_list_with_post_and_search_advanced_must_not(client):
    resp = client.post('/api/flow/search', json={'selectedFilter': 'test_search_advanced_must_not'})
    assert len(resp.json) == 1 and resp.json[0]['request']['host'] == 'www.meituan.com'


def test_flow_list_with_post_and_search_both_advanced_condition(client):
    resp = client.post('/api/flow/search', json={'selectedFilter': 'test_search_both_advanced_condition'})
    assert len(resp.json) == 1 and resp.json[0]['request']['host'] == 'www.meituan.com'


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
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_DECODE


def test_flow_with_id_and_decode_input_decode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'i.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_decode=true')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_DECODE


def test_flow_with_id_and_decode_use_capital_letter_true(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_decode=True')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_DECODE


def test_flow_with_id_and_decode_use_capital_letter_false(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_decode=FALSE')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_ENCODE


def test_flow_with_id_and_no_decode_input_encode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_ENCODE


def test_flow_with_id_and_no_decode_input_decode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'i.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_DECODE
