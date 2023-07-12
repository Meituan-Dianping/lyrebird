import pytest
from lyrebird import application
from lyrebird.config import ConfigManager
from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder

_conf = {
    'ip': '127.0.0.1',
    'mock.port': 9090
}

test_word_encode = r'%E4%BD%A0%E5%A5%BD%EF%BC%8C%E4%B8%96%E7%95%8C'
test_word_decode = '你好，世界'

application._cm = ConfigManager()
application._cm.config = _conf
application.encoders_decoders = EncoderDecoder()
server = LyrebirdMockServer()
server.app.testing = True

with server.app.test_client() as client:
    client.delete('/api/flow', json={'idx': ''})
    client.get('/mock/http://i.meituan.com')
    client.get('/mock/http://www.baidu.com')

@pytest.fixture
def client():
    application._cm = ConfigManager()
    application._cm.config = _conf
    application.encoders_decoders = EncoderDecoder()
    server = LyrebirdMockServer()
    server.app.testing = True

    client = server.app.test_client()
    ctx = server.app.app_context()
    ctx.push()
    yield client
    ctx.pop()


def test_flow_list_with_get(client):
    resp = client.get('/api/flow')
    assert len(resp.json) == 2


def test_flow_list_with_post_and_search_simple(client):
    resp = client.post('/api/flow/search', json={'selectedFilter': {
                                                    'ignore': [
                                                        'www.baidu.com'
                                                    ]
                                                }})
    assert len(resp.json) == 1 and resp.json[0]['request']['url'] != 'http://www.baidu.com'


def test_flow_list_with_post_and_search_advanced_must(client):
    resp = client.post('/api/flow/search', json={'selectedFilter': {
                                                    'advanced': {
                                                            'must': {
                                                                'request.url': [
                                                                    'www.baidu.com'
                                                                ]
                                                        }
                                                    }
                                                }})
    assert len(resp.json) == 1 and resp.json[0]['request']['url'] == 'http://www.baidu.com'


def test_flow_list_with_post_and_search_advanced_must_not(client):
    resp = client.post('/api/flow/search', json={'selectedFilter': {
                                                    'advanced': {
                                                            'must_not': {
                                                                'request.url': [
                                                                    'www.baidu.com'
                                                                ]
                                                        }
                                                    }
                                                }})
    assert len(resp.json) == 1 and resp.json[0]['request']['url'] != 'http://www.baidu.com'


def test_flow_with_id(client):
    flow_id = client.get('/api/flow').json[0]['id']
    resp = client.get(f'/api/flow/{flow_id}')
    assert resp.json['code'] == 1000


def test_flow_with_id_and_decode1(client):
    client.get(f'/mock/http://i.meituan.com?word={test_word_encode}')
    flow_id = client.get('/api/flow').json[0]['id']
    resp = client.get(f'/api/flow/{flow_id}?is_decode=true')
    assert  resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == test_word_decode


def test_flow_with_id_and_decode2(client):
    client.get(f'/mock/http://i.meituan.com?word={test_word_decode}')
    flow_id = client.get('/api/flow').json[0]['id']
    resp = client.get(f'/api/flow/{flow_id}?is_decode=true')
    assert  resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == test_word_decode


def test_flow_with_id_and_no_decode1(client):
    client.get(f'/mock/http://i.meituan.com?word={test_word_decode}')
    flow_id = client.get('/api/flow').json[0]['id']
    resp = client.get(f'/api/flow/{flow_id}')
    assert  resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == test_word_decode


def test_flow_with_id_and_no_decode2(client):
    client.get(f'/mock/http://i.meituan.com?word={test_word_encode}')
    flow_id = client.get('/api/flow').json[0]['id']
    resp = client.get(f'/api/flow/{flow_id}')
    assert  resp.json['code'] == 1000 and resp.json['data']['request']['query']['word'] == test_word_encode
