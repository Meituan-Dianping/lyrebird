import pytest
from lyrebird import application
from lyrebird.mock import context
from lyrebird.config import ConfigManager
from lyrebird.checker import LyrebirdCheckerServer
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

FILENAME = 'encoder_decoder.py'

CONTENT = u'''
from lyrebird import encoder, decoder

@encoder(rules={'request.url': ''})
def test_func(flow):
    flow['request']['headers']['modify_by_encoder_decoder'] = 'encode'

@decoder(rules={'request.url': ''})
def test_func(flow):
    flow['request']['headers']['modify_by_encoder_decoder'] = 'decode'
    '''

_conf = {
    'ip': '127.0.0.1',
    'mock.port': 9090,
    'inspector.filters': TEST_FILTER,
    'checker.workspace': '',
    'checker.switch': {
        FILENAME: True
    },
    'event.lyrebird_metrics_report': False
}


def get_server():
    application._cm = ConfigManager()
    application._cm.config = _conf
    application.encoders_decoders = EncoderDecoder()
    server = LyrebirdMockServer()
    server.app.testing = True
    return server


@pytest.fixture(scope='module', autouse=True)
def setup_and_teardown_environment():
    with get_server().app.test_client() as init_client:
        context.application.cache._cache.clear()
        for url in REQUEST_URL:
            init_client.get(url)
    yield


@pytest.fixture
def checker_server(tmp_path, tmpdir):
    encoder_decoder_file = tmp_path / FILENAME
    encoder_decoder_file.write_text(CONTENT)
    _conf['checker.workspace'] = tmp_path
    _conf['root'] = tmpdir
    _conf['ROOT'] = tmpdir

    server = LyrebirdCheckerServer()
    server.start()
    server.SCRIPTS_DIR = tmp_path
    application.server['checker'] = server
    application.encoders_decoders = EncoderDecoder()
    yield server
    server.stop()


@pytest.fixture
def client(checker_server):
    server = get_server()
    with server.app.test_client() as client:
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
    resp = client.get(f'/api/flow/{flow_id}?no_decode=0')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_DECODE


def test_flow_with_id_and_decode_input_decode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'i.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?no_decode=0')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_DECODE


def test_flow_with_id_and_not_decode_input_encode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?no_decode=1')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_ENCODE


def test_flow_with_id_and_not_decode_input_decode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'i.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?no_decode=1')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_DECODE


def test_flow_with_id_and_default_input_encode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_DECODE


def test_flow_with_id_and_default_input_decode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'i.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}')
    assert resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == TEST_WORD_DECODE


def test_flow_with_id_and_origin(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_origin=true')
    assert resp.json['code'] == 1000 
    assert 'modify_by_encoder_decoder' not in resp.json['data']['request']['headers']


def test_flow_with_id_and_not_origin(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_origin=false')
    assert resp.json['code'] == 1000
    assert 'modify_by_encoder_decoder' in resp.json['data']['request']['headers']
    assert resp.json['data']['request']['headers']['modify_by_encoder_decoder'] == 'decode'


def test_flow_with_id_and_origin_capital(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_origin=TRUE')
    assert resp.json['code'] == 1000
    assert 'modify_by_encoder_decoder' not in resp.json['data']['request']['headers']


def test_flow_with_id_and_not_origin_capital(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_origin=False')
    assert resp.json['code'] == 1000
    assert 'modify_by_encoder_decoder' in resp.json['data']['request']['headers']


def test_flow_with_id_and_origin_and_decode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_origin=true&no_decode=0')
    assert resp.json['code'] == 1000 
    assert 'modify_by_encoder_decoder' not in resp.json['data']['request']['headers']
    assert resp.json['data']['request']['query']['word'] == TEST_WORD_DECODE


def test_flow_with_id_and_not_origin_and_decode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_origin=false&no_decode=0')
    assert resp.json['code'] == 1000
    assert 'modify_by_encoder_decoder' in resp.json['data']['request']['headers']
    assert resp.json['data']['request']['query']['word'] == TEST_WORD_DECODE


def test_flow_with_id_and_origin_and_not_decode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_origin=true&no_decode=1')
    assert resp.json['code'] == 1000 
    assert 'modify_by_encoder_decoder' not in resp.json['data']['request']['headers']
    assert resp.json['data']['request']['query']['word'] == TEST_WORD_ENCODE


def test_flow_with_id_and_not_origin_and_not_decode(client):
    flow_id = None
    flows = client.get('/api/flow').json
    for flow in flows:
        if flow['request']['host'] == 'm.meituan.com':
            flow_id = flow['id']
            break
    resp = client.get(f'/api/flow/{flow_id}?is_origin=false&no_decode=1')
    assert resp.json['code'] == 1000
    assert 'modify_by_encoder_decoder' in resp.json['data']['request']['headers']
    assert resp.json['data']['request']['query']['word'] == TEST_WORD_ENCODE
