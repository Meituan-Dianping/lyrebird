import pytest
import codecs
import json
from pathlib import Path
from lyrebird.mock import dm

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


dataC = {
    'id': 'dataC-UUID',
    'name': 'dataC',
    'rule': {
        'request.url': '/api/detail'
    },
    'request': {
        'url': 'http://unittest.com/api/detail'
    }
}

dataD = {
    'id': 'dataD-UUID',
    'name': 'dataD',
    'rule': {
        'request.url': '/api/detail'
    },
    'request': {
        'url': 'http://unittest.com/api/detail'
    }
}


prop = {
    'children': [
        {
            'id': 'groupA-UUID',
            'name': 'groupA',
            'type': 'group',
            'children': [
                {
                    'id': 'dataA-UUID',
                    'name': 'dataA',
                    'type': 'data'
                },
                {
                    'id': 'dataB-UUID',
                    'name': 'dataB',
                    'type': 'data'
                },
            ]
        },
        {
            'id': 'groupB-UUID',
            'name': 'groupB',
            'type': 'group',
            'children': [
                {
                    'id': 'dataC-UUID',
                    'name': 'dataC',
                    'type': 'data'
                },
            ]
        },
        {
            'id': 'groupC-UUID',
            'name': 'groupC',
            'type': 'group'
        },
        {
            'id': 'groupD-UUID',
            'name': 'groupD',
            'type': 'group',
            'children': [
                {
                    'id': 'dataD-UUID',
                    'name': 'dataD',
                    'type': 'data'
                }
            ]
        }
    ]
}


@pytest.fixture
def root(tmpdir):
    with codecs.open(tmpdir / 'dataA-UUID', 'w') as f:
        json.dump(dataA, f)
    with codecs.open(tmpdir / 'dataB-UUID', 'w') as f:
        json.dump(dataB, f)
    with codecs.open(tmpdir / 'dataC-UUID', 'w') as f:
        json.dump(dataC, f)
    with codecs.open(tmpdir / 'dataD-UUID', 'w') as f:
        json.dump(dataD, f)
    with codecs.open(tmpdir / '.lyrebird_prop', 'w') as f:
        json.dump(prop, f)
    return tmpdir


@pytest.fixture
def data_manager(root):
    _dm = dm.DataManager()
    _dm.set_root(root)
    return _dm


def test_load_from_path(root):
    _dm = dm.DataManager()
    _dm.set_root(root)

    assert 'dataA-UUID' in _dm.id_map
    assert 'dataB-UUID' in _dm.id_map
    assert 'dataC-UUID' in _dm.id_map
    assert 'groupA-UUID' in _dm.id_map
    assert 'groupB-UUID' in _dm.id_map
    assert 'groupC-UUID' in _dm.id_map


def test_activate(data_manager):
    data_manager.activate('groupA-UUID')
    assert len(data_manager.activated_data) == 2
    assert 'dataA-UUID' in data_manager.activated_data
    assert 'dataB-UUID' in data_manager.activated_data


def test_mock_rule(data_manager):
    flow = {
        'request': {
            'url': 'http://somehost/api/search'
        }
    }
    mock_data_list = data_manager.get_matched_data(flow)
    assert len(mock_data_list) == 0

    data_manager.activate('groupA-UUID')
    mock_data_list = data_manager.get_matched_data(flow)
    assert len(mock_data_list) == 1

    data_manager.deactivate()
    data_manager.activate('groupB-UUID')
    mock_data_list = data_manager.get_matched_data(flow)
    assert len(mock_data_list) == 0


def test_activate_groups(data_manager):
    flow_A = {
        'request': {
            'url': 'http://somehost/api/search'
        }
    }
    flow_B = {
        'request': {
            'url': 'http://somehost/api/detail'
        }
    }
    data_manager.activate('groupA-UUID')
    data_manager.activate('groupB-UUID')
    flow_A_mock_data = data_manager.get_matched_data(flow_A)
    flow_B_mock_data = data_manager.get_matched_data(flow_B)
    assert len(flow_A_mock_data) == 1
    assert len(flow_B_mock_data) == 1


def test_conflict_checker(data_manager):
    data_manager.activate('groupB-UUID')
    conflict_rules = data_manager.check_conflict()
    assert len(conflict_rules) == 0

    data_manager.activate('groupD-UUID')
    conflict_rules = data_manager.check_conflict()
    assert len(conflict_rules) == 2
