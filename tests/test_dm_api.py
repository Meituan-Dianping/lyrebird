import json
import pytest
import codecs
import lyrebird
from typing import NamedTuple
from lyrebird import application
from lyrebird.mock import context
from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird.mock.dm.file_data_adapter import data_adapter
from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder


dataA = {
    'id': 'dataA-UUID',
    'name': 'dataA',
    'rule': {
        'request.url': '/api/search'
    },
    'request': {
        'url': 'http://unittest.com/api/search'
    }
}

prop = {
    'id': 'root',
    'name': 'root',
    'type': 'group',
    'parent_id': None,
    'children': [{
        'id': 'groupA-UUID',
        'name': 'groupA',
        'type': 'group',
        'parent_id': 'root',
        'children': [
            {
                'id': 'dataA-UUID',
                'name': 'dataA',
                'type': 'data',
                'parent_id': 'groupA-UUID'
            }
        ]
    }]
}


MockConfigManager = NamedTuple('MockConfigManager', [('config', dict)])


class FakeSocketio:

    def emit(self, event, *args, **kwargs): {
        print(f'Send event {event} args={args} kw={kwargs}')
    }


@pytest.fixture
def root(tmpdir):
    with codecs.open(tmpdir / 'dataA-UUID', 'w') as f:
        json.dump(dataA, f)
    with codecs.open(tmpdir / '.lyrebird_prop', 'w') as f:
        json.dump(prop, f)
    return tmpdir


@pytest.fixture
def client(root, tmpdir):
    _conf = {
        'ip': '127.0.0.1',
        'mock.port': 9090
    }
    application._cm = MockConfigManager(config=_conf)
    lyrebird.mock.context.application.socket_io = FakeSocketio()
    application.encoders_decoders = EncoderDecoder()

    server = LyrebirdMockServer()
    client = server.app.test_client()
    _dm = context.application.data_manager
    _dm.snapshot_workspace = tmpdir
    _dm.set_adapter(data_adapter)
    _dm.set_root(root)
    yield client


def test_group_get_with_group_id(client):
    group_id = 'groupA-UUID'
    resp = client.get(f'/api/group/{group_id}')
    assert resp.json['code'] == 1000


def test_group_get_children(client):
    group_id = 'groupA-UUID'
    resp = client.get(f'/api/group/{group_id}?childrenOnly=true')
    assert resp.json['code'] == 1000
    data = resp.json['data']
    assert len(data) == 1


def test_group_get_without_group_id(client):
    resp = client.get('/api/group')
    assert resp.json['code'] == 1000


def test_group_post(client):
    resp = client.post('/api/group', json={
        'data': {
            'name': 'groupA-UUID',
            'parent_id': 'root'
        },
        'id': 'groupJ-UUID'
    })
    assert resp.json['code'] == 1000


def test_group_put(client):
    resp = client.put('/api/group', json={
        'data': {
            'name': 'groupA-UUID-new',
            'parent_id': 'root'
        },
        'id': 'groupA-UUID'
    })
    assert resp.json['code'] == 1000


def test_group_delete_with_group_id(client):
    group_id = 'groupA-UUID'
    resp = client.delete(f'/api/group/{group_id}')
    assert resp.json['code'] == 1000


def test_group_delete_with_query(client):
    resp = client.delete('/api/group', json={
        'query': {
            'id': ['groupA-UUID']
        }
    })
    assert resp.json['code'] == 1000


def test_data_get(client):
    data_id = 'dataA-UUID'
    resp = client.get(f'/api/data/{data_id}')
    assert resp.json['code'] == 1000


def test_data_put(client):
    resp = client.put('/api/data', json={
        'id': 'dataA-UUID',
        'name': 'dataA-new',
        'rule': {
            'request.data.sort': None,
            'request.url': '(?=.*search)'
        },
        'request': {
            'url': 'http://unittest.com/api/detail'
        }
    })
    assert resp.json['code'] == 1000


def test_data_post(client):
    resp = client.post('/api/data', json={
        'id': 'dataB-UUID',
        'name': 'dataB',
        'parent_id': 'root',
        'data':
            {
                'id': 'dataB-UUID',
                'name': 'dataB',
                'rule': {
                    'request.data.sort': None,
                    'request.url': '(?=.*search)'
                },
                'request': {
                    'url': 'http://unittest.com/api/detail'
                }
            }
    })
    assert resp.json['code'] == 1000


def test_data_delete(client):
    data_id = 'dataA-UUID'
    resp = client.delete(f'/api/data/{data_id}')
    assert resp.json['code'] == 1000


def test_data_activate(client):
    data_id = 'dataA-UUID'
    action = 'activate'
    resp = client.put(f'/api/mock/{data_id}/{action}')
    assert resp.json['code'] == 1000


def test_data_activate_with_info(client):
    data_id = 'dataA-UUID'
    action = 'activate'
    resp = client.put(f'/api/mock/{data_id}/{action}', json={
        'info': {
            'a': 1
        }
    })
    assert resp.json['code'] == 1000


def test_data_activate_without_body(client):
    data_id = 'dataA-UUID'
    action = 'activate'
    resp = client.put(f'/api/mock/{data_id}/{action}', headers={'Content-Type': 'application/json'})
    assert resp.json['code'] == 1000


def test_data_deactivate(client):
    data_id = 'dataA-UUID'
    action = 'deactivate'
    resp = client.put(f'/api/mock/{data_id}/{action}')
    assert resp.json['code'] == 1000
