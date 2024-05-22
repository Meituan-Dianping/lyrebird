import time
import pytest
from lyrebird import application
from lyrebird.config import ConfigManager
from lyrebird.mock.mock_server import LyrebirdMockServer

_conf = {
    'ip': '127.0.0.1',
    'mock.port': 9090,
    'custom_key': 'custom_value',
    'config.value.tojsonKey': ['custom.[a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12}'],
    'custom.8df051be-4381-41b6-9252-120d9b558bf6': {"custom_key": "custom_value"},
    'event.lyrebird_metrics_report': False
}

origin_data = '"keyA":"valueA","keyB":"{{config.get(\'custom.8df051be-4381-41b6-9252-120d9b558bf6\')}}","keyC":"valueC","keyD":"{{today}}"'
render_response_data_tojson = '"keyA":"valueA","keyB":{"custom_key": "custom_value"},"keyC":"valueC","keyD":"'
render_response_data_not_tojson = '"keyA":"valueA","keyB":"' + "{'custom_key': 'custom_value'}" + '","keyC":"valueC","keyD":"'

@pytest.fixture
def client():
    application._cm = ConfigManager()
    application._cm.config = _conf
    server = LyrebirdMockServer()
    with server.app.test_client() as client:
        yield client
    server.terminate()

def test_render_api_without_json(client):
    resp = client.put('/api/render')
    assert resp.json['code'] == 3000

def test_render_api_without_enable_tojson(client):
    resp = client.put('/api/render', json={
        'data': origin_data
    })
    today = time.strftime('%Y-%m-%d', time.localtime())
    assert resp.json['code'] == 1000
    assert resp.json['data'] == render_response_data_tojson + today + '"'

def test_render_api_with_enable_tojson_true(client):
    resp = client.put('/api/render', json={
        'data': origin_data,
        'enable_tojson': True
    })
    today = time.strftime('%Y-%m-%d', time.localtime())
    assert resp.json['code'] == 1000
    assert resp.json['data'] == render_response_data_tojson + today + '"'

def test_render_api_with_data_None(client):
    resp = client.put('/api/render', json={
        'data': '',
        'enable_tojson': True
    })
    assert resp.json['code'] == 1000
    assert resp.json['data'] == ''

def test_render_api_with_enable_tojson_false(client):
    resp = client.put('/api/render', json={
        'data': origin_data,
        'enable_tojson': False
    })
    today = time.strftime('%Y-%m-%d', time.localtime())
    assert resp.json['code'] == 1000
    assert resp.json['data'] == render_response_data_not_tojson + today + '"'
