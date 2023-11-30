import re
import json
import pytest
import codecs
import tarfile
import lyrebird
from pathlib import Path
from copy import deepcopy
from typing import NamedTuple
from urllib.parse import urlparse
from lyrebird.mock import dm
from lyrebird.mock.dm.file_data_adapter import data_adapter
from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder
from lyrebird import application

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

dataB = {
    'id': 'dataB-UUID',
    'name': 'dataB',
    'rule': {
        'request.url': '/api/location'
    },
    'request': {
        'url': 'http://unittest.com/api/location'
    }
}


prop = {
    'id': 'root',
    'name': 'root',
    'type': 'group',
    'parent_id': None,
    'children': [
        {
            'id': 'groupA-UUID',
            'name': 'groupA',
            'type': 'group',
            'parent_id': 'root',
            'super_id': 'groupB-UUID',
            'children': [
                {
                    'id': 'dataA-UUID',
                    'name': 'dataA',
                    'type': 'data',
                    'parent_id': 'groupA-UUID'
                },
                {
                    'id': 'dataB-UUID',
                    'name': 'dataB',
                    'type': 'data',
                    'parent_id': 'groupA-UUID'
                },
            ]
        }
    ]
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
    with codecs.open(tmpdir / 'dataB-UUID', 'w') as f:
        json.dump(dataB, f)
    with codecs.open(tmpdir / '.lyrebird_prop', 'w') as f:
        json.dump(prop, f)
    return tmpdir


@pytest.fixture
def data_manager(root, tmpdir):
    _conf = {
        'ip': '127.0.0.1',
        'mock.port': 9090,
    }
    application._cm = MockConfigManager(config=_conf)
    lyrebird.mock.context.application.socket_io = FakeSocketio()
    application.encoders_decoders = EncoderDecoder()
    _dm = dm.DataManager()
    _dm.snapshot_workspace = tmpdir
    _dm.set_adapter(data_adapter)
    _dm.set_root(root)

    data = {
        'request': {
            'url': 'http://somehost/api/detail',
            'headers': {}
        },
        'response': {
            'headers': {},
            'data': {},
            'code': 200
        }
    }
    _dm.temp_mock_tree.add_data(data)
    return _dm


def test_get(data_manager):
    root = data_manager.temp_mock_tree.get()
    assert root['id'] == 'tmp_group'
    assert root['type'] == 'group'
    assert root['name'] == 'Temp Mock'
    assert len(root['children']) == 1


def test_match(data_manager):
    flow_a = {
        'request': {
            'url': 'http://somehost/api/search'
        }
    }
    flow_a_mock_data = data_manager.temp_mock_tree.get_matched_data(flow_a)
    assert len(flow_a_mock_data) == 0

    flow_b = {
        'request': {
            'url': 'http://somehost/api/detail'
        }
    }
    flow_b_mock_data = data_manager.temp_mock_tree.get_matched_data(flow_b)
    assert len(flow_b_mock_data) == 1


def test_add(data_manager):
    data = {
        'request': {
            'url': 'http://hostname.com/pathA/pathB?param=1'
        },
        'response': {}
    }
    new_data_id = data_manager.temp_mock_tree.add_data(data)
    assert new_data_id

    found_new_data = False
    for child in data_manager.temp_mock_tree.root['children']:
        if child['id'] == new_data_id:
            found_new_data = True
            break
    assert found_new_data

    assert new_data_id in data_manager.temp_mock_tree.activated_data


def test_add(data_manager):
    data = {
        'request': {
            'url': 'http://hostname.com/pathA/pathB?param=1'
        },
        'response': {}
    }
    new_data_id = data_manager.temp_mock_tree.add_data(data)
    assert new_data_id

    found_new_data = False
    for child in data_manager.temp_mock_tree.root['children']:
        if child['id'] == new_data_id:
            found_new_data = True
            break
    assert found_new_data

    assert new_data_id in data_manager.temp_mock_tree.activated_data

    parsed_url = urlparse(data['request']['url'])
    parsed_url_path = parsed_url.path

    _new_data = data_manager.temp_mock_tree.activated_data.get(new_data_id)
    assert parsed_url_path in _new_data['name']
    assert f'(?=.*{parsed_url_path}\?)' == _new_data['rule']['request.url']


# new
def test_add_data_request_url_no_params(data_manager):
    data = {
        'request': {
            'url': f'http://hostname.com/pathA/pathB'
        },
        'response': {}
    }
    new_data_id = data_manager.temp_mock_tree.add_data(data)
    assert new_data_id

    found_new_data = False
    for child in data_manager.temp_mock_tree.root['children']:
        if child['id'] == new_data_id:
            found_new_data = True
            break
    assert found_new_data

    assert new_data_id in data_manager.temp_mock_tree.activated_data

    parsed_url = urlparse(data['request']['url'])
    parsed_url_path = parsed_url.path

    _new_data = data_manager.temp_mock_tree.activated_data.get(new_data_id)
    assert parsed_url_path in _new_data['name']

    assert f'(?=.*{parsed_url_path}$)' == _new_data['rule']['request.url']


def test_add_data_request_url_no_path(data_manager):
    data = {
        'request': {
            'url': f'http://hostname.com'
        },
        'response': {}
    }
    new_data_id = data_manager.temp_mock_tree.add_data(data)
    assert new_data_id

    found_new_data = False
    for child in data_manager.temp_mock_tree.root['children']:
        if child['id'] == new_data_id:
            found_new_data = True
            break
    assert found_new_data

    assert new_data_id in data_manager.temp_mock_tree.activated_data

    parsed_url = urlparse(data['request']['url'])
    parsed_url_hostname = parsed_url.hostname

    _new_data = data_manager.temp_mock_tree.activated_data.get(new_data_id)
    assert parsed_url_hostname in _new_data['name']

    assert f'(?=.*{parsed_url_hostname}$)' == _new_data['rule']['request.url']


def test_add_data_request_url_illegal(data_manager):
    url_illegal = 'EXAMPLE'
    data = {
        'request': {
            'url': url_illegal
        },
        'response': {}
    }
    new_data_id = data_manager.temp_mock_tree.add_data(data)
    assert new_data_id

    found_new_data = False
    for child in data_manager.temp_mock_tree.root['children']:
        if child['id'] == new_data_id:
            found_new_data = True
            break
    assert found_new_data

    assert new_data_id in data_manager.temp_mock_tree.activated_data

    _new_data = data_manager.temp_mock_tree.activated_data.get(new_data_id)
    assert url_illegal in _new_data['name']

    assert f'(?=.*{url_illegal})' == _new_data['rule']['request.url']


def test_delete_by_query(data_manager):
    data = {
        'request': {
            'url': 'http://hostname.com/pathA/pathB?param=1',
            'headers': {}
        },
        'response': {
            'headers': {},
            'data': {},
            'code': 200
        }
    }
    new_data_id = data_manager.temp_mock_tree.add_data(data)
    assert new_data_id

    query = {
        'id': [new_data_id]
    }
    data_manager.temp_mock_tree.delete_by_query(query)
    found_delete_data = False
    for child in data_manager.temp_mock_tree.root['children']:
        if child['id'] == new_data_id:
            found_delete_data = True
            break
    assert found_delete_data == False

    assert new_data_id not in data_manager.temp_mock_tree.activated_data
