import pytest
import codecs
import json
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
    'id': 'root',
    'parent_id': None,
    'children': [
        {
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
                },
                {
                    'id': 'dataB-UUID',
                    'name': 'dataB',
                    'type': 'data',
                    'parent_id': 'groupA-UUID'
                },
            ]
        },
        {
            'id': 'groupB-UUID',
            'name': 'groupB',
            'type': 'group',
            'parent_id': 'root',
            'children': [
                {
                    'id': 'dataC-UUID',
                    'name': 'dataC',
                    'type': 'data',
                    'parent_id': 'groupB-UUID'
                },
            ]
        },
        {
            'id': 'groupC-UUID',
            'name': 'groupC',
            'type': 'group',
            'parent_id': 'root',
            'children': []
        },
        {
            'id': 'groupD-UUID',
            'name': 'groupD',
            'type': 'group',
            'parent_id': 'root',
            'children': [
                {
                    'id': 'dataD-UUID',
                    'name': 'dataD',
                    'type': 'data',
                    'parent_id': 'groupD-UUID'
                }
            ]
        },
        {
            'id': 'groupE-UUID',
            'name': 'groupE',
            'type': 'group',
            'parent_id': 'root',
            'children': [
                {
                    'id': 'dataC-UUID',
                    'name': 'dataC',
                    'type': 'data',
                    'parent_id': 'groupE-UUID'
                },
                {
                    'id': 'dataD-UUID',
                    'name': 'dataD',
                    'type': 'data',
                    'parent_id': 'groupE-UUID'
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
    conflict_rules = data_manager.activated_data_check_conflict()
    assert len(conflict_rules) == 0

    data_manager.activate('groupD-UUID')
    conflict_rules = data_manager.activated_data_check_conflict()
    assert len(conflict_rules) == 2

    conflict_rules = data_manager.check_conflict('groupE-UUID')
    assert len(conflict_rules) == 2


def test_add_group(data_manager):
    new_group_id = data_manager.add_group(None, 'root_group')
    assert new_group_id in data_manager.id_map
    found_new_group = False
    for child in data_manager.root['children']:
        if child['id'] == new_group_id:
            found_new_group = True
            break
    assert found_new_group


def test_add_data(data_manager):
    data = {
        'name': 'add_data_name',
        'request': {},
        'response': {}
    }
    new_data_id = data_manager.add_data('groupC-UUID', data)
    _new_data = data_manager.id_map.get(new_data_id)
    assert data == _new_data
    group_c = data_manager.id_map.get('groupC-UUID')
    found_new_data = False
    for child in group_c['children']:
        if child['id'] == new_data_id:
            found_new_data = True
            break
    assert found_new_data
    new_data_file = data_manager.root_path / new_data_id
    assert new_data_file.exists()


def test_delete(data_manager):
    data_manager.delete('groupB-UUID')
    assert 'groupB-UUID' not in data_manager.id_map
    assert 'dataC-UUID' not in data_manager.id_map
    data_file = data_manager.root_path / 'dataC-UUID'
    assert not data_file.exists()


def test_cut_and_paste(data_manager):
    data_manager.cut('groupA-UUID')
    data_manager.paste('groupC-UUID')
    assert 'groupA-UUID' in data_manager.id_map
    group_a = data_manager.id_map.get('groupA-UUID')
    assert group_a['parent_id'] == 'groupC-UUID'
    group_c = data_manager.id_map.get('groupC-UUID')
    assert group_a in group_c['children']


def test_copy_and_paste(data_manager):
    data_manager.copy('groupA-UUID')
    data_manager.paste('groupC-UUID')
    assert 'groupA-UUID' in data_manager.id_map
    group_c = data_manager.id_map.get('groupC-UUID')
    assert len(group_c['children']) == 1
    new_group = group_c['children'][0]
    assert new_group['id'] != 'groupA-UUID'
    assert new_group['name'] == 'groupA'
