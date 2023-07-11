import pytest
import codecs
import json
from copy import deepcopy
import lyrebird
from lyrebird.mock import dm
from lyrebird.event import EventServer
from lyrebird.config import ConfigManager
from lyrebird.checker import LyrebirdCheckerServer
from lyrebird.config import CONFIG_TREE_SHOW_CONFIG
from lyrebird.mock.dm.file_data_adapter import data_adapter
from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder
from lyrebird import application


data_a = {
    'id': 'dataA-UUID',
    'name': 'dataA',
    'rule': {
        'request.url': '/api/search'
    },
    'request': {
        'url': 'http://unittest.com/api/search'
    }
}

data_b = {
    'id': 'dataB-UUID',
    'name': '.Settings',
    'json': '{\n    \"checker.switch\": {\n        \"checker_a.py\": true,\n        \"checker_b.py\": false\n    }\n}'
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
            'children': [
                {
                    'id': 'dataA-UUID',
                    'name': 'dataA',
                    'type': 'data',
                    'parent_id': 'groupA-UUID'
                },
                {
                    'id': 'dataB-UUID',
                    'name': '.Settings',
                    'type': 'config',
                    'parent_id': 'groupA-UUID'
                },
            ]
        },
        {
            'id': 'groupB-UUID',
            'name': 'groupC',
            'type': 'group',
            'parent_id': 'root',
            'children': []
        }
    ]
}


class FakeSocketio:

    def emit(self, event, *args, **kwargs): {
        print(f'Send event {event} args={args} kw={kwargs}')
    }


@pytest.fixture
def root(tmpdir):
    with codecs.open(tmpdir / 'dataA-UUID', 'w') as f:
        json.dump(data_a, f)
    with codecs.open(tmpdir / 'dataB-UUID', 'w') as f:
        json.dump(data_b, f)
    with codecs.open(tmpdir / '.lyrebird_prop', 'w') as f:
        json.dump(prop, f)
    return tmpdir


@pytest.fixture
def data_manager(root, tmpdir):
    conf = {
        'version': '0.10.4',
        'proxy.filters': ['kuxun', 'meituan', 'sankuai', 'dianping'],
        'proxy.port': 4272,
        'mock.port': 9090,
        'ip': '127.0.0.1',
        'mock.data': 'data',
        'mock.proxy_headers': {
            'scheme': 'MKScheme',
            'host': 'MKOriginHost',
            'port': 'MKOriginPort'
        }
    }
    application._cm = ConfigManager()
    lyrebird.mock.context.application.socket_io = FakeSocketio()
    application.encoders_decoders = EncoderDecoder()
    _dm = dm.DataManager()
    _dm.snapshot_workspace = tmpdir
    _dm.set_adapter(data_adapter)
    _dm.set_root(root)
    return _dm



CHECKER_A_FILENAME = 'checker_a.py'
CHECKER_B_FILENAME = 'checker_b.py'
CHECKER_A_SWITCH = False
CHECKER_B_SWITCH = True

CONTENT = u"from lyrebird import event\n@event('flow')\ndef test_func():\n\tpass"

@pytest.fixture
def checker_init(tmp_path, tmpdir):
    config = {
        'checker.workspace': tmp_path,
        'checker.switch': {
            CHECKER_A_FILENAME: CHECKER_A_SWITCH,
            CHECKER_B_FILENAME: CHECKER_B_SWITCH
        }
    }

    checker_a_file = tmp_path / CHECKER_A_FILENAME
    checker_a_file.write_text(CONTENT)
    checker_b_file = tmp_path / CHECKER_B_FILENAME
    checker_b_file.write_text(CONTENT)

    application._cm.config.update(config)

    return application.checkers

@pytest.fixture
def checker_server(checker_init, tmp_path):
    server = LyrebirdCheckerServer()
    server.start()
    server.SCRIPTS_DIR = tmp_path
    application.server['checker'] = server
    yield server
    server.stop()


@pytest.fixture
def event_server():
    server = EventServer()
    application.server['event'] = server
    yield server


def test_get_all_group_close_show_config(data_manager):
    data_manager.reload()
    dm_root_child = set([c['id'] for c in data_manager.root['children']])
    prop_root_child = set([c['id'] for c in prop['children']])
    assert dm_root_child == prop_root_child

    dm_group_a_child = set([c['id'] for c in data_manager.id_map['groupA-UUID']['children']])
    prop_group_a_child = set([c['id'] for c in prop['children'][0]['children']])
    assert dm_group_a_child == prop_group_a_child - set(['dataB-UUID'])


def test_get_all_group_open_show_config(data_manager):
    application._cm.config[CONFIG_TREE_SHOW_CONFIG] = True
    data_manager.reload()

    dm_root_children = data_manager.root['children']
    dm_group_a_children = data_manager.id_map['groupA-UUID']['children']
    dm_group_b_children = data_manager.id_map['groupB-UUID']['children']

    prop_root_children = prop['children']
    prop_gruop_a_children = prop_root_children[0]['children']
    prop_gruop_b_children = prop_root_children[1]['children']

    dm_child_id = set([c['id'] for c in dm_root_children])
    prop_child_id = set([c['id'] for c in prop_root_children])
    assert len(prop_child_id - dm_child_id) == 0
    assert len(dm_child_id - prop_child_id) == 1

    dm_child_id = set([c['id'] for c in dm_group_a_children])
    prop_child_id = set([c['id'] for c in prop_gruop_a_children])
    assert prop_child_id == dm_child_id

    dm_child_id = set([c['id'] for c in dm_group_b_children])
    prop_child_id = set([c['id'] for c in prop_gruop_b_children])
    assert len(prop_child_id - dm_child_id) == 0
    assert len(dm_child_id - prop_child_id) == 1

    application._cm.config[CONFIG_TREE_SHOW_CONFIG] = False
    data_manager.reload()

    dm_root_children = data_manager.root['children']
    dm_group_a_children = data_manager.id_map['groupA-UUID']['children']
    dm_group_b_children = data_manager.id_map['groupB-UUID']['children']

    prop_root_children = prop['children']
    prop_gruop_a_children = prop_root_children[0]['children']
    prop_gruop_b_children = prop_root_children[1]['children']

    dm_child_id = set([c['id'] for c in dm_root_children])
    prop_child_id = set([c['id'] for c in prop_root_children])
    assert prop_child_id == dm_child_id

    dm_child_id = set([c['id'] for c in dm_group_a_children])
    prop_child_id = set([c['id'] for c in prop_gruop_a_children])
    assert dm_child_id == prop_child_id - set(['dataB-UUID'])

    dm_child_id = set([c['id'] for c in dm_group_b_children])
    prop_child_id = set([c['id'] for c in prop_gruop_b_children])
    assert prop_child_id == dm_child_id


def test_get_group_children_close_show_config(data_manager):
    children = data_manager._get_group_children('root')
    assert len(children) == 2

    children = data_manager._get_group_children('groupA-UUID')
    assert len(children) == 2 - 1

    children = data_manager._get_group_children('groupB-UUID')
    assert len(children) == 0


def test_get_group_children_open_show_config(data_manager):
    application._cm.config[CONFIG_TREE_SHOW_CONFIG] = True

    children = data_manager._get_group_children('root')
    assert len(children) == 2 + 1

    children = data_manager._get_group_children('groupA-UUID')
    assert len(children) == 2

    children = data_manager._get_group_children('groupB-UUID')
    assert len(children) == 0 + 1

    application._cm.config[CONFIG_TREE_SHOW_CONFIG] = False

    children = data_manager._get_group_children('root')
    assert len(children) == 2

    children = data_manager._get_group_children('groupA-UUID')
    assert len(children) == 2 - 1

    children = data_manager._get_group_children('groupB-UUID')
    assert len(children) == 0


def test_add_config_name(data_manager):
    application._cm.config[CONFIG_TREE_SHOW_CONFIG] = True
    data_manager.reload()

    group = data_manager.id_map['groupB-UUID']
    config_id = group['children'][0]['id']
    data = data_manager.id_map[config_id]

    new_data = deepcopy(data)
    new_data['name'] = 'dataB-new-name'
    data_manager.update_data(config_id, new_data)

    assert data_manager.id_map[config_id]['name'] == '.Settings'


def test_activate_with_config_contains_extension(data_manager, event_server, checker_server):
    assert application.checkers[CHECKER_A_FILENAME].activated  == False
    assert application.checkers[CHECKER_B_FILENAME].activated == True
    data_manager.activate('groupA-UUID')

    assert application.checkers[CHECKER_A_FILENAME].activated  == True
    assert application.checkers[CHECKER_B_FILENAME].activated == False
