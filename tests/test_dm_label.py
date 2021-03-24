import pytest
import codecs
import json
from typing import NamedTuple
from lyrebird.mock import dm
from lyrebird.mock.dm import label as lb
from lyrebird import application
from lyrebird.mock import context
from lyrebird.mock.dm.file_data_adapter import FileDataAdapter

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

label_a = {'name':'label_a','color':'red','description':'description label_a'}
label_b = {'name':'label_b','color':'green','description':'description label_b'}

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
            'children': [
                {
                    'id': 'groupB-UUID',
                    'label': [label_a, label_b],
                    'name': 'groupB',
                    'type': 'group',
                    'parent_id': 'groupA-UUID',
                    'children': [
                        {
                            'id': 'dataA-UUID',
                            'name': 'dataA',
                            'type': 'data',
                            'parent_id': 'groupB-UUID'
                        }
                    ]
                }
            ]
        },
        {
            'id': 'groupC-UUID',
            'label': [label_a],
            'name': 'groupC',
            'type': 'group',
            'parent_id': 'root',
            'children': []
        }
    ]
}


MockConfigManager = NamedTuple('MockConfigManager', [('config', dict)])


@pytest.fixture
def root(tmpdir):
    with codecs.open(tmpdir / 'dataA-UUID', 'w') as f:
        json.dump(dataA, f)
    with codecs.open(tmpdir / '.lyrebird_prop', 'w') as f:
        json.dump(prop, f)
    return tmpdir


@pytest.fixture
def data_manager(root):
    _conf = {
        'ip': '127.0.0.1',
        'mock.port': 9090
    }
    application._cm = MockConfigManager(config=_conf)
    _dm = dm.DataManager()
    _dm.set_adapter(FileDataAdapter)
    _dm.set_root(root)
    context.application.data_manager = _dm
    return _dm


@pytest.fixture
def label_handler(root):
    _label_handler = lb.LabelHandler()
    return _label_handler


def test_get_label(data_manager, label_handler):
    label_handler.get_label(data_manager.root)

    assert len(label_handler.label_map) == 2

    label_a_id = label_handler._get_label_name_md5(label_a)
    label_b_id = label_handler._get_label_name_md5(label_b)

    assert label_a_id in label_handler.label_map
    assert label_b_id in label_handler.label_map

    assert len(label_handler.label_map[label_a_id]['groups']) == 2
    assert len(label_handler.label_map[label_b_id]['groups']) == 1


def test_create_label(data_manager, label_handler):
    label_handler.get_label(data_manager.root)

    label_name = 'new_label'
    label_color = '#666666'
    label_description = 'description new_label'
    create_label = {
        'name': label_name,
        'color': label_color,
        'description': label_description
    }
    label_handler.create_label(create_label)

    label_id = label_handler._get_label_name_md5(create_label)

    assert label_id in label_handler.isolated_label_ids

    assert len(label_handler.label_map) == 3
    assert label_id in label_handler.label_map
    assert label_handler.label_map[label_id]['id'] == label_id
    assert label_handler.label_map[label_id]['name'] == label_name
    assert label_handler.label_map[label_id]['color'] == label_color
    assert label_handler.label_map[label_id]['description'] == label_description

    label_handler.get_label(data_manager.root)

    assert label_id in label_handler.isolated_label_ids

    assert len(label_handler.label_map) == 3
    assert label_id in label_handler.label_map


def test_update_label(data_manager, label_handler):
    label_handler.get_label(data_manager.root)

    old_label_id = label_handler._get_label_name_md5({'name':'label_a'})

    label_name = 'new_label'
    label_color = '#666666'
    label_description = 'description new_label'
    update_label = {
        'id': old_label_id,
        'name': label_name,
        'color': label_color,
        'description': label_description
    }

    label_handler.update_label(update_label)

    new_label_id = label_handler._get_label_name_md5(update_label)

    assert old_label_id not in label_handler.label_map
    assert new_label_id in label_handler.label_map

    assert len(label_handler.label_map) == 2
    assert label_handler.label_map[new_label_id]['id'] == new_label_id
    assert label_handler.label_map[new_label_id]['name'] == label_name
    assert label_handler.label_map[new_label_id]['color'] == label_color
    assert label_handler.label_map[new_label_id]['description'] == label_description

    groupB = data_manager.id_map.get('groupB-UUID')
    groupB_label = [
        {'name':'label_b', 'color':'green', 'description':'description label_b'},
        {'name':label_name, 'color':label_color, 'description':label_description}
    ]
    assert json.dumps(groupB['label']) == json.dumps(groupB_label)

    groupC = data_manager.id_map.get('groupC-UUID')
    groupC_label = [
        {'name':label_name, 'color':label_color, 'description':label_description}
    ]
    assert json.dumps(groupC['label']) == json.dumps(groupC_label)


def test_delete_label(data_manager, label_handler):
    label_handler.get_label(data_manager.root)

    label_id = label_handler._get_label_name_md5({'name':'label_a'})

    label_handler.delete_label(label_id)

    assert label_id not in label_handler.label_map
    assert len(label_handler.label_map) == 1

    groupB = data_manager.id_map.get('groupB-UUID')
    groupB_label = [
        {'name':'label_b', 'color':'green', 'description':'description label_b'}
    ]
    assert json.dumps(groupB['label']) == json.dumps(groupB_label)

    groupC = data_manager.id_map.get('groupC-UUID')
    groupC_label = []
    assert json.dumps(groupC['label']) == json.dumps(groupC_label)


def test_delete_isolated_label(data_manager, label_handler):
    label_handler.get_label(data_manager.root)

    label_name = 'new_label'
    label_color = '#666666'
    label_description = 'description new_label'
    create_label = {
        'name': label_name,
        'color': label_color,
        'description': label_description
    }
    label_handler.create_label(create_label)

    label_id = label_handler._get_label_name_md5(create_label)
    label_handler.delete_label(label_id)

    assert label_id not in label_handler.label_map
    assert label_id not in label_handler.isolated_label_ids
    assert len(label_handler.label_map) == 2
    assert len(label_handler.isolated_label_ids) == 0
