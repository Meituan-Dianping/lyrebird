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

dataF = {
    'id': 'dataF-UUID',
    'name': 'dataF',
    'rule': {
        'request.data.poi[*].name': '(?=.*app)',
        'request.url': '(?=.*search)'
    },
    'request': {
        'url': 'http://unittest.com/api/detail'
    }
}

dataG = {
    'id': 'dataG-UUID',
    'name': 'dataG',
    'rule': {
        'request.data.sort': 1,
        'request.url': '(?=.*search)'
    },
    'request': {
        'url': 'http://unittest.com/api/detail'
    }
}

dataH = {
    'id': 'dataH-UUID',
    'name': 'dataH',
    'rule': {
        'request.data.sort': True,
        'request.url': '(?=.*search)'
    },
    'request': {
        'url': 'http://unittest.com/api/detail'
    }
}

dataI = {
    'id': 'dataI-UUID',
    'name': 'dataI',
    'rule': {
        'request.data.sort': None,
        'request.url': '(?=.*search)'
    },
    'request': {
        'url': 'http://unittest.com/api/detail'
    }
}

dataJ = {
    'id': 'dataJ-UUID',
    'name': 'dataJ',
    'rule': {
        'request.url': '/api/search'
    },
    'request': {
        'url': 'http://unittest.com/api/search'
    },
    'response': {
        'data': '{"keyA":"valueA","keyB":"{{config.get(\'custom.8df051be-4381-41b6-9252-120d9b558bf6\')}}","keyC":"valueC"}'
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
        },
        {
            'id': 'groupB-UUID',
            'name': 'groupB',
            'type': 'group',
            'parent_id': 'root',
            'super_id': 'groupC-UUID',
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
            'super_id': 'groupD-UUID',
            'children': []
        },
        {
            'id': 'groupD-UUID',
            'name': 'groupD',
            'type': 'group',
            'parent_id': 'root',
            'super_id': 'groupE-UUID',
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
        },
        {
            'id': 'groupF-UUID',
            'name': 'groupF',
            'type': 'group',
            'parent_id': 'root',
            'children': [
                {
                    'id': 'groupG-UUID',
                    'name': 'groupG',
                    'type': 'group',
                    'parent_id': 'groupF-UUID',
                    'children': [
                        {
                            'id': 'groupH-UUID',
                            'label': [label_a, label_b],
                            'name': 'groupH',
                            'type': 'group',
                            'parent_id': 'groupG-UUID',
                            'children': []
                        }
                    ]
                },
                {
                    'id': 'groupI-UUID',
                    'label': [label_a],
                    'name': 'groupI',
                    'type': 'group',
                    'parent_id': 'groupF-UUID',
                    'children': [
                        {
                            'id': 'dataD-UUID',
                            'name': 'dataD',
                            'type': 'data',
                            'parent_id': 'groupI-UUID'
                        }
                    ]
                }
            ]
        },
        {
            'id': 'groupJ-UUID',
            'name': 'groupJ',
            'type': 'group',
            'parent_id': 'root',
            'children': [
                {
                    'id': 'dataF-UUID',
                    'name': 'dataF',
                    'type': 'data',
                    'parent_id': 'groupJ-UUID'
                },
                {
                    'id': 'dataG-UUID',
                    'name': 'dataG',
                    'type': 'data',
                    'parent_id': 'groupJ-UUID'
                },
                {
                    'id': 'dataH-UUID',
                    'name': 'dataH',
                    'type': 'data',
                    'parent_id': 'groupJ-UUID'
                },
                {
                    'id': 'dataI-UUID',
                    'name': 'dataI',
                    'type': 'data',
                    'parent_id': 'groupJ-UUID'
                },
            ]
        },
        {
            'id': 'groupK-UUID',
            'name': 'groupK',
            'type': 'group',
            'parent_id': 'root',
            'children': [
                {
                    'id': 'dataJ-UUID',
                    'name': 'dataJ',
                    'type': 'data',
                    'parent_id': 'groupK-UUID'
                },
            ]
        }
    ]
}

snapshot = {
    'snapshot': {
        'id': 'groupA-UUID',
        'parent_id': None,
        'super_id': 'groupB-UUID',
        'name': 'groupA',
        'type': 'group',
        'children': [
            {
                'id': 'dataA-UUID',
                'name': 'dataA',
                'type': 'data',
                'parent_id': 'snapshotA-UUID'
            },
            {
                'id': 'dataB-UUID',
                'name': 'dataB',
                'type': 'data',
                'parent_id': 'groupA-UUID'
            }
        ]
    },
    'events': [
        dataA,
        dataB
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
    with codecs.open(tmpdir / 'dataC-UUID', 'w') as f:
        json.dump(dataC, f)
    with codecs.open(tmpdir / 'dataD-UUID', 'w') as f:
        json.dump(dataD, f)
    with codecs.open(tmpdir / 'dataF-UUID', 'w') as f:
        json.dump(dataF, f)
    with codecs.open(tmpdir / 'dataG-UUID', 'w') as f:
        json.dump(dataG, f)
    with codecs.open(tmpdir / 'dataH-UUID', 'w') as f:
        json.dump(dataH, f)
    with codecs.open(tmpdir / 'dataI-UUID', 'w') as f:
        json.dump(dataI, f)
    with codecs.open(tmpdir / 'dataJ-UUID', 'w') as f:
        json.dump(dataJ, f)
    with codecs.open(tmpdir / '.lyrebird_prop', 'w') as f:
        json.dump(prop, f)
    return tmpdir


@pytest.fixture
def data_manager(root, tmpdir):
    _conf = {
        'ip': '127.0.0.1',
        'mock.port': 9090,
        'config.value.tojsonKey': ['custom.[a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12}'],
        'custom.8df051be-4381-41b6-9252-120d9b558bf6': {"key": "value"}
    }
    application._cm = MockConfigManager(config=_conf)
    lyrebird.mock.context.application.socket_io = FakeSocketio()
    application.encoders_decoders = EncoderDecoder()
    _dm = dm.DataManager()
    _dm.snapshot_workspace = tmpdir
    _dm.set_adapter(data_adapter)
    _dm.set_root(root)
    return _dm


def test_load_from_path(root):
    _conf = {
        'ip': '127.0.0.1',
        'mock.port': 9090,
        'config.value.tojsonKey': ['custom.[a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12}'],
        'custom.8df051be-4381-41b6-9252-120d9b558bf6': {"key": "value"}
    }
    application._cm = MockConfigManager(config=_conf)

    _dm = dm.DataManager()
    _dm.set_adapter(data_adapter)
    _dm.set_root(root)

    assert 'dataA-UUID' in _dm.id_map
    assert 'dataB-UUID' in _dm.id_map
    assert 'dataC-UUID' in _dm.id_map
    assert 'groupA-UUID' in _dm.id_map
    assert 'groupB-UUID' in _dm.id_map
    assert 'groupC-UUID' in _dm.id_map


def test_load(data_manager):
    data_manager.reload()
    assert 'dataA-UUID' in data_manager.id_map
    assert 'dataB-UUID' in data_manager.id_map
    assert 'dataC-UUID' in data_manager.id_map
    assert 'groupA-UUID' in data_manager.id_map
    assert 'groupB-UUID' in data_manager.id_map
    assert 'groupC-UUID' in data_manager.id_map


def test_activate(data_manager):
    data_manager.activate('groupE-UUID')
    assert len(data_manager.activated_data) == 2
    assert 'dataC-UUID' in data_manager.activated_data
    assert 'dataD-UUID' in data_manager.activated_data


def test_activate_with_request_data_rule(data_manager):
    data_manager.activate('groupJ-UUID')
    assert data_manager.is_activated_data_rules_contains_request_data == True
    data_manager.deactivate()
    assert data_manager.is_activated_data_rules_contains_request_data == False
    data_manager.activate('groupA-UUID')
    assert data_manager.is_activated_data_rules_contains_request_data == False


def test_activate_with_super_id(data_manager):
    data_manager.activate('groupA-UUID')

    groupA_children_length = len(data_manager.id_map['groupA-UUID']['children'])
    groupB_children_length = len(data_manager.id_map['groupB-UUID']['children'])
    groupC_children_length = len(data_manager.id_map['groupC-UUID']['children'])
    groupD_children_length = len(data_manager.id_map['groupD-UUID']['children'])
    activated_data_length = groupA_children_length + groupB_children_length + groupC_children_length +\
        groupD_children_length
    assert activated_data_length == len(data_manager.activated_data)
    assert 'dataA-UUID' in data_manager.activated_data
    assert 'dataB-UUID' in data_manager.activated_data
    assert 'dataC-UUID' in data_manager.activated_data
    assert 'dataD-UUID' in data_manager.activated_data

def test_activate_with_tojson(data_manager):
    flow = {
        'request': {
            'url': 'http://somehost/api/search'
        }
    }
    data_manager.activate('groupK-UUID')
    mock_data_list = data_manager.get_matched_data(flow)
    response_data = mock_data_list[0]['response']['data']
    tojson_str = '{"key": "value"}'
    assert tojson_str in response_data

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


def test_mock_rule_with_jsonpath(data_manager):
    flowA = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                "poi":[
                    {"name":"app"},
                    {"name":"apple"}
                ]
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowA)
    assert len(mock_data_list) == 0

    data_manager.activate('groupJ-UUID')
    mock_data_list = data_manager.get_matched_data(flowA)
    assert len(mock_data_list) == 1

    flowB = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                "poi":[
                    {"name":"app"},
                    {"name":"banana"}
                ]
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowB)
    assert len(mock_data_list) == 0


def test_mock_rule_number_with_jsonpath(data_manager):
    flowA = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': 1
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowA)
    assert len(mock_data_list) == 0

    data_manager.activate('groupJ-UUID')
    mock_data_list = data_manager.get_matched_data(flowA)
    assert len(mock_data_list) == 1

    flowB = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': 1.0
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowB)
    assert len(mock_data_list) == 0

    flowC = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': 222
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowC)
    assert len(mock_data_list) == 0

    flowD = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': '1'
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowD)
    assert len(mock_data_list) == 0


def test_mock_rule_bool_with_jsonpath(data_manager):
    flowA = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': True
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowA)
    assert len(mock_data_list) == 0

    data_manager.activate('groupJ-UUID')
    mock_data_list = data_manager.get_matched_data(flowA)
    assert len(mock_data_list) == 1

    flowB = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': False
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowB)
    assert len(mock_data_list) == 0

    flowC = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': 'True'
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowC)
    assert len(mock_data_list) == 0


def test_mock_rule_null_with_jsonpath(data_manager):
    flowA = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': None
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowA)
    assert len(mock_data_list) == 0

    data_manager.activate('groupJ-UUID')
    mock_data_list = data_manager.get_matched_data(flowA)
    assert len(mock_data_list) == 1

    flowB = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': ''
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowB)
    assert len(mock_data_list) == 0

    flowC = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': 'None'
            }
        }
    }
    mock_data_list = data_manager.get_matched_data(flowC)
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
    assert len(flow_A_mock_data) == 0
    assert len(flow_B_mock_data) == 1


def test_activate_groups_with_extra_info(data_manager):
    flow_A = {
        'request': {
            'url': 'http://somehost/api/search'
        }
    }
    data_manager.activate('groupA-UUID', info={'a': 1})
    flow_A_mock_data = data_manager.get_matched_data(flow_A)
    assert len(flow_A_mock_data) == 1


def test_conflict_checker(data_manager):
    data_manager.activate('groupB-UUID')
    conflict_rules = data_manager.activated_data_check_conflict()
    assert len(conflict_rules) == 2
    data_manager.deactivate()

    data_manager.activate('groupD-UUID')
    conflict_rules = data_manager.activated_data_check_conflict()
    assert len(conflict_rules) == 2
    data_manager.deactivate()

    data_manager.activate('groupJ-UUID')
    conflict_rules = data_manager.activated_data_check_conflict()
    assert len(conflict_rules) == 0
    data_manager.deactivate()

    conflict_rules = data_manager.check_conflict('groupE-UUID')
    assert len(conflict_rules) == 2


def test_get_group_children(data_manager):
    children = data_manager._get_group_children('groupF-UUID')
    assert len(children) == 2

    children = data_manager._get_group_children('groupG-UUID')
    assert len(children) == 1


def test_add_group(data_manager):
    new_group_id = data_manager.add_group({
        'name': 'root_group',
        'parent_id': None
    })
    assert new_group_id in data_manager.id_map
    found_new_group = False
    for child in data_manager.root['children']:
        if child['id'] == new_group_id:
            found_new_group = True
            break
    assert found_new_group

def test_add_group_by_path(data_manager):
    new_group_id = data_manager.add_group_by_path('/groupA')
    assert new_group_id in data_manager.id_map
    found_new_group = False
    for child in data_manager.root['children']:
        if child['id'] == new_group_id:
            found_new_group = True
            break
    assert found_new_group


def test_add_data_no_type(data_manager):
    custom_name = 'CUSTOM_NAME'
    custom_rule = {
        'CUSTOM_KEY': 'CUSTOM_VALUE'
    }
    data = {
        'name': custom_name,
        'rule': custom_rule,
        'request': {
            'url': 'http://hostname.com/pathA/pathB?param=1'
        },
        'response': {}
    }

    new_data_id = data_manager.add_data('groupC-UUID', data)
    _new_data_node = data_manager.id_map.get(new_data_id)
    assert custom_name == _new_data_node['name']
    _new_data = data_manager.get(new_data_id)
    assert custom_name == _new_data['name']

    assert custom_rule == _new_data['rule']

    assert data['request'] == _new_data['request']
    group_c = data_manager.id_map.get('groupC-UUID')
    found_new_data = False
    for child in group_c['children']:
        if child['id'] == new_data_id:
            found_new_data = True
            break
    assert found_new_data
    new_data_file = data_manager.root_path / new_data_id
    assert new_data_file.exists()


def test_add_data_request_with_name_rule(data_manager):
    custom_name = 'CUSTOM_NAME'
    custom_rule = {
        'CUSTOM_KEY': 'CUSTOM_VALUE'
    }
    data = {
        'name': custom_name,
        'type': 'data',
        'rule': custom_rule,
        'request': {
            'url': 'http://hostname.com/pathA/pathB?param=1'
        },
        'response': {}
    }

    new_data_id = data_manager.add_data('groupC-UUID', data)
    _new_data_node = data_manager.id_map.get(new_data_id)
    assert custom_name == _new_data_node['name']
    _new_data = data_manager.get(new_data_id)
    assert custom_name == _new_data['name']

    assert custom_rule == _new_data['rule']

    assert data['request'] == _new_data['request']
    group_c = data_manager.id_map.get('groupC-UUID')
    found_new_data = False
    for child in group_c['children']:
        if child['id'] == new_data_id:
            found_new_data = True
            break
    assert found_new_data
    new_data_file = data_manager.root_path / new_data_id
    assert new_data_file.exists()


def test_add_data_request_url_params(data_manager):
    data = {
        'type': 'data',
        'request': {
            'url': f'http://hostname.com/pathA/pathB?param=1'
        },
        'response': {}
    }
    parsed_url = urlparse(data['request']['url'])
    parsed_url_path = parsed_url.path

    new_data_id = data_manager.add_data('groupC-UUID', data)
    _new_data_node = data_manager.id_map.get(new_data_id)
    assert parsed_url_path == _new_data_node['name']
    _new_data = data_manager.get(new_data_id)
    assert parsed_url_path == _new_data['name']

    assert f'(?=.*{parsed_url_path}\?)' == _new_data['rule']['request.url']

    assert data['request'] == _new_data['request']
    group_c = data_manager.id_map.get('groupC-UUID')
    found_new_data = False
    for child in group_c['children']:
        if child['id'] == new_data_id:
            found_new_data = True
            break
    assert found_new_data
    new_data_file = data_manager.root_path / new_data_id
    assert new_data_file.exists()


def test_add_data_request_url_no_params(data_manager):
    data = {
        'type': 'data',
        'request': {
            'url': f'http://hostname.com/pathA/pathB'
        },
        'response': {}
    }
    parsed_url = urlparse(data['request']['url'])
    parsed_url_path = parsed_url.path

    new_data_id = data_manager.add_data('groupC-UUID', data)
    _new_data_node = data_manager.id_map.get(new_data_id)
    assert parsed_url_path == _new_data_node['name']
    _new_data = data_manager.get(new_data_id)
    assert parsed_url_path == _new_data['name']

    assert f'(?=.*{parsed_url_path}$)' == _new_data['rule']['request.url']


def test_add_data_request_url_no_path(data_manager):
    data = {
        'type': 'data',
        'request': {
            'url': f'http://hostname.com'
        },
        'response': {}
    }
    parsed_url = urlparse(data['request']['url'])
    parsed_url_hostname = parsed_url.hostname

    new_data_id = data_manager.add_data('groupC-UUID', data)
    _new_data_node = data_manager.id_map.get(new_data_id)
    assert parsed_url_hostname == _new_data_node['name']
    _new_data = data_manager.get(new_data_id)
    assert parsed_url_hostname == _new_data['name']

    assert f'(?=.*{parsed_url_hostname}$)' == _new_data['rule']['request.url']


def test_add_data_request_url_illegal(data_manager):
    url_illegal = 'EXAMPLE'
    data = {
        'type': 'data',
        'request': {
            'url': url_illegal
        },
        'response': {}
    }

    new_data_id = data_manager.add_data('groupC-UUID', data)
    _new_data_node = data_manager.id_map.get(new_data_id)
    assert url_illegal == _new_data_node['name']
    _new_data = data_manager.get(new_data_id)
    assert url_illegal == _new_data['name']

    assert f'(?=.*{url_illegal})' == _new_data['rule']['request.url']


def test_add_data_no_request(data_manager):
    data = {
        'name': 'add_data_name',
        'type': 'data'
    }
    new_data_id = data_manager.add_data('groupC-UUID', data)
    _new_data_node = data_manager.id_map.get(new_data_id)
    assert data['name'] == _new_data_node['name']
    _new_data = data_manager.get(new_data_id)
    assert data['name'] == _new_data['name']
    group_c = data_manager.id_map.get('groupC-UUID')
    found_new_data = False
    for child in group_c['children']:
        if child['id'] == new_data_id:
            found_new_data = True
            break
    assert found_new_data
    new_data_file = data_manager.root_path / new_data_id
    assert new_data_file.exists()


def test_add_json(data_manager):
    data = {
        'name': 'add_json_name',
        'type': 'json',
        'json': {"a" : 1}
    }
    new_data_id = data_manager.add_data('groupC-UUID', data)
    _new_data_node = data_manager.id_map.get(new_data_id)
    assert data['name'] == _new_data_node['name']
    _new_data = data_manager.get(new_data_id)
    assert data['name'] == _new_data['name']
    group_c = data_manager.id_map.get('groupC-UUID')
    found_new_data = False
    for child in group_c['children']:
        if child['id'] == new_data_id:
            found_new_data = True
            break
    assert found_new_data
    new_data_file = data_manager.root_path / new_data_id
    assert new_data_file.exists()


def test_update_group_change_value(data_manager):
    new_group_name = 'groupA-new-name'
    update_group_id = 'groupA-UUID'

    update_data = deepcopy(data_manager.id_map[update_group_id])
    update_data['name'] = new_group_name
    data_manager.update_group(update_group_id, update_data)

    assert data_manager.id_map[update_group_id]['name'] == new_group_name


def test_update_group_key_add_and_delete(data_manager):
    new_group_key = 'groupA-new-info'
    new_group_value = 'groupA-new-value'
    update_group_id = 'groupA-UUID'


    update_data = deepcopy(data_manager.id_map[update_group_id])
    update_data[new_group_key] = new_group_value
    data_manager.update_group(update_group_id, update_data)

    assert new_group_key in data_manager.id_map[update_group_id]
    assert data_manager.id_map[update_group_id][new_group_key] == new_group_value

    update_data.pop(new_group_key)
    data_manager.update_group(update_group_id, update_data)

    assert new_group_key not in data_manager.id_map[update_group_id]


def test_update_data(data_manager):
    new_data_name = 'groupA-new-name'
    update_data_id = 'dataA-UUID'

    update_data = deepcopy(dataA)
    update_data['name'] = new_data_name
    data_manager.update_data(update_data_id, update_data)

    assert data_manager.id_map[update_data_id]['name'] == new_data_name
    assert data_manager.get(update_data_id)['name'] == new_data_name


def test_delete(data_manager):
    data_manager.delete('groupB-UUID')
    assert 'groupB-UUID' not in data_manager.id_map
    assert 'dataC-UUID' not in data_manager.id_map
    data_file = data_manager.root_path / 'dataC-UUID'
    assert not data_file.exists()


def test_delete_by_query(data_manager):
    query = {
        'id': ['groupB-UUID', 'dataC-UUID']
    }
    data_manager.delete_by_query(query)
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
    assert new_group['name'] == 'groupA - copy'


def test_duplicate_group(data_manager):
    group_f = data_manager.id_map.get('groupF-UUID')
    origin_group_f_children_count = len(group_f['children'])

    data_manager.duplicate('groupI-UUID')
    assert len(group_f['children']) == origin_group_f_children_count + 1
    children_name_list = [i['name'] for i in group_f['children']]
    assert 'groupI - copy' in children_name_list


def test_duplicate_data(data_manager):
    group_i = data_manager.id_map.get('groupI-UUID')
    origin_group_i_children_count = len(group_i['children'])

    data_manager.duplicate('dataD-UUID')
    assert len(group_i['children']) == origin_group_i_children_count + 1
    children_name_list = [i['name'] for i in group_i['children']]
    assert 'dataD - copy' in children_name_list


def test_prop_writer():
    prop_writer = dm.file_data_adapter.PropWriter()
    prop_str = prop_writer.parse(
        {
            "url": "<\"test\">",
            "description": "a\nb\nc"
        }
    )
    assert prop_str == '{"url":"<\\"test\\">","description":"a\\nb\\nc"}'
    json.loads(prop_str)


def test_prop_writer_with_dict_ignore_key(data_manager):
    prop_str_correct = '{"id":"root","name":"root","type":"group","parent_id":null,"children":[\n  {"id":"groupA-UUID","name":"groupA","type":"group","parent_id":"root","super_id":"groupB-UUID","children":[\n    {"id":"dataA-UUID","name":"dataA","type":"data","parent_id":"groupA-UUID"},\n    {"id":"dataB-UUID","name":"dataB","type":"data","parent_id":"groupA-UUID"}]},\n  {"id":"groupB-UUID","name":"groupB","type":"group","parent_id":"root","super_id":"groupC-UUID","children":[\n    {"id":"dataC-UUID","name":"dataC","type":"data","parent_id":"groupB-UUID"}]},\n  {"id":"groupC-UUID","name":"groupC","type":"group","parent_id":"root","super_id":"groupD-UUID","children":[]},\n  {"id":"groupD-UUID","name":"groupD","type":"group","parent_id":"root","super_id":"groupE-UUID","children":[\n    {"id":"dataD-UUID","name":"dataD","type":"data","parent_id":"groupD-UUID"}]},\n  {"id":"groupE-UUID","name":"groupE","type":"group","parent_id":"root","children":[\n    {"id":"dataC-UUID","name":"dataC","type":"data","parent_id":"groupE-UUID"},\n    {"id":"dataD-UUID","name":"dataD","type":"data","parent_id":"groupE-UUID"}]},\n  {"id":"groupF-UUID","name":"groupF","type":"group","parent_id":"root","children":[\n    {"id":"groupG-UUID","name":"groupG","type":"group","parent_id":"groupF-UUID","children":[\n      {"id":"groupH-UUID","label":[{"name":"label_a","color":"red","description":"description label_a"},{"name":"label_b","color":"green","description":"description label_b"}],"name":"groupH","type":"group","parent_id":"groupG-UUID","children":[]}]},\n    {"id":"groupI-UUID","label":[{"name":"label_a","color":"red","description":"description label_a"}],"name":"groupI","type":"group","parent_id":"groupF-UUID","children":[\n      {"id":"dataD-UUID","name":"dataD","type":"data","parent_id":"groupI-UUID"}]}]},\n  {"id":"groupJ-UUID","name":"groupJ","type":"group","parent_id":"root","children":[\n    {"id":"dataF-UUID","name":"dataF","type":"data","parent_id":"groupJ-UUID"},\n    {"id":"dataG-UUID","name":"dataG","type":"data","parent_id":"groupJ-UUID"},\n    {"id":"dataH-UUID","name":"dataH","type":"data","parent_id":"groupJ-UUID"},\n    {"id":"dataI-UUID","name":"dataI","type":"data","parent_id":"groupJ-UUID"}]},\n  {"id":"groupK-UUID","name":"groupK","type":"group","parent_id":"root","children":[\n    {"id":"dataJ-UUID","name":"dataJ","type":"data","parent_id":"groupK-UUID"}]}]}'

    prop_writer = dm.file_data_adapter.PropWriter()
    prop_writer.dict_ignore_key.update(data_manager.unsave_keys)
    prop_str = prop_writer.parse(data_manager.root)

    pattern = r'{"id":"[0-9a-fA-F-]+","name":".Settings","type":"config","parent_id":"root"},\n  '
    prop_str = re.sub(pattern, '', prop_str)

    assert prop_str == prop_str_correct
    new_prop = json.loads(prop_str)
    assert prop == new_prop


def test_make_data_map_by_group(data_manager):
    group_set = set(['groupH-UUID', 'groupI-UUID'])

    node = data_manager.make_data_map_by_group(group_set)

    prop = {
        'id': 'root',
        'name': 'root',
        'type': 'group',
        'parent_id': None,
        'children': [
            {
                'id': 'groupF-UUID',
                'name': 'groupF',
                'type': 'group',
                'parent_id': 'root',
                'children': [
                    {
                        'id': 'groupG-UUID',
                        'name': 'groupG',
                        'type': 'group',
                        'parent_id': 'groupF-UUID',
                        'children': [
                            {
                                'id': 'groupH-UUID',
                                'label': [label_a, label_b],
                                'name': 'groupH',
                                'type': 'group',
                                'parent_id': 'groupG-UUID',
                                'children': []
                            }
                        ]
                    },
                    {
                        'id': 'groupI-UUID',
                        'label': [label_a],
                        'name': 'groupI',
                        'type': 'group',
                        'parent_id': 'groupF-UUID',
                        'children': [
                            {
                                'id': 'dataD-UUID',
                                'name': 'dataD',
                                'type': 'data',
                                'parent_id': 'groupJ-UUID'
                            }
                        ]
                    }
                ]
            }
        ]
    }
    prop_writer = dm.file_data_adapter.PropWriter()
    prop_writer.dict_ignore_key.update(data_manager.unsave_keys)
    node_str = prop_writer.parse(node)
    prop_str = prop_writer.parse(prop)
    assert len(node_str) == len(prop_str)

def test_export_from_local(data_manager, tmpdir):
    def pop_id(node):
        if 'id' in node:
            node.pop('id')
        if 'parent_id' in node:
            node.pop('parent_id')
        if 'parent' in node:
            node.pop('parent')
        if 'abs_parent_path' in node:
            node.pop('abs_parent_path')
        if 'response' in node and not node['response']:
            node.pop('response')
        for child in node.get('children', []):
            pop_id(child)
        return node

    group_id, filename = data_manager.export_from_local(snapshot)
    children = data_manager.get(group_id)['children']
    assert group_id in data_manager.id_map
    assert len(children) == len(snapshot['events'])

    output_path = Path(tmpdir) / 'test'
    tf = tarfile.open(str(filename))
    tf.extractall(str(output_path))
    tf.close()

    children_set = set([group_id] + [i['id'] for i in children])
    file_set = set()
    for file_ in output_path.iterdir():
        with codecs.open(file_, 'r', 'utf-8') as f:
            data = json.load(f)
        if file_.name == '.lyrebird_prop':
            snapshot_data = snapshot['snapshot']
            data_id = group_id
        else:
            snapshot_data = [e for e in snapshot['events'] if e['name']==data['name']][0]
            data_id = data['id']

        file_set.add(data['id'])
        assert data == data_manager.get(data_id)
        assert data['id'] != snapshot_data['id']
        data_pop_id = pop_id(deepcopy(data))
        snapshot_data_pop_id = pop_id(deepcopy(snapshot_data))
        assert data_pop_id == snapshot_data_pop_id

    assert file_set == children_set

def test_export_from_remote(data_manager, tmpdir):
    def pop_id(node):
        if 'id' in node:
            node.pop('id')
        if 'parent_id' in node:
            node.pop('parent_id')
        if 'parent' in node:
            node.pop('parent')
        if 'abs_parent_path' in node:
            node.pop('abs_parent_path')
        if 'response' in node and not node['response']:
            node.pop('response')
        for child in node.get('children', []):
            pop_id(child)
        return node

    group_id = 'groupA-UUID'
    filename = data_manager.export_from_remote(group_id)
    children = data_manager.get(group_id)['children']
    assert Path(filename).exists()

    output_path = Path(tmpdir) / 'test'
    tf = tarfile.open(str(filename))
    tf.extractall(str(output_path))
    tf.close()

    children_set = set([group_id] + [i['id'] for i in children])
    file_set = set()
    for file_ in output_path.iterdir():
        with codecs.open(file_, 'r', 'utf-8') as f:
            data = json.load(f)
        if file_.name == '.lyrebird_prop':
            snapshot_data = snapshot['snapshot']
            data_id = group_id
        else:
            snapshot_data = [e for e in snapshot['events'] if e['name']==data['name']][0]
            data_id = data['id']

        file_set.add(data['id'])
        assert data == data_manager.get(data_id)
        assert data['id'] == snapshot_data['id']
        data_pop_id = pop_id(deepcopy(data))
        snapshot_data_pop_id = pop_id(deepcopy(snapshot_data))
        assert data_pop_id == snapshot_data_pop_id

    assert file_set == children_set


def test_import_from_local(data_manager):
    group_id, filename = data_manager.export_from_local(snapshot)
    children = data_manager.get(group_id)['children']
    assert group_id in data_manager.id_map
    assert len(children) == len(snapshot['events'])


def test_import_from_file(data_manager, tmpdir):

    def pop_id(node):
        if 'id' in node:
            node.pop('id')
        if 'parent_id' in node:
            node.pop('parent_id')
        if 'parent' in node:
            node.pop('parent')
        if 'abs_parent_path' in node:
            node.pop('abs_parent_path')
        if 'response' in node and not node['response']:
            node.pop('response')
        for child in node.get('children', []):
            pop_id(child)
        return node

    group_id = 'groupA-UUID'
    filename = data_manager.export_from_remote(group_id)
    group = data_manager.get(group_id)

    new_group_id = data_manager.import_from_file('root', filename)
    new_group = data_manager.get(new_group_id)

    for new_group_child in new_group['children']:
        new_group_child_data = data_manager.get(new_group_child['id'])
        group_child = [c for c in group['children'] if c['name']==new_group_child['name']][0]
        group_child_data = data_manager.get(group_child['id'])

        pop_id(new_group_child_data)
        pop_id(group_child_data)

        assert new_group_child_data == group_child_data

    group_pop_id = pop_id(deepcopy(group))
    new_group_pop_id = pop_id(deepcopy(new_group))
    assert group_pop_id == new_group_pop_id


def test_get_snapshot_file_detail(data_manager):
    group_id = 'groupB-UUID'
    filename = data_manager.export_from_remote(group_id)

    snapshot_info, output_path = data_manager.get_snapshot_file_detail(filename)
    assert snapshot_info == data_manager.id_map.get(group_id)
