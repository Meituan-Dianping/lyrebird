import pytest
import codecs
import json
import tarfile
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlparse
from lyrebird.mock import dm
from lyrebird.mock.dm.file_data_adapter import data_adapter
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
            ]
        }
    ]
}


MockConfigManager = NamedTuple('MockConfigManager', [('config', dict)])


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
    with codecs.open(tmpdir / '.lyrebird_prop', 'w') as f:
        json.dump(prop, f)
    return tmpdir


@pytest.fixture
def data_manager(root, tmpdir):
    _conf = {
        'ip': '127.0.0.1',
        'mock.port': 9090
    }
    application._cm = MockConfigManager(config=_conf)
    _dm = dm.DataManager()
    _dm.SNAPSHOT_WORKSPACE = tmpdir
    _dm.set_adapter(data_adapter)
    _dm.set_root(root)
    return _dm


def test_load_from_path(root):
    _dm = dm.DataManager()
    _dm.set_adapter(data_adapter)
    _dm.set_root(root)

    assert 'dataA-UUID' in _dm.id_map
    assert 'dataB-UUID' in _dm.id_map
    assert 'dataC-UUID' in _dm.id_map
    assert 'groupA-UUID' in _dm.id_map
    assert 'groupB-UUID' in _dm.id_map
    assert 'groupC-UUID' in _dm.id_map


def test_activate(data_manager):
    data_manager.activate('groupE-UUID')
    assert len(data_manager.activated_data) == 2
    assert 'dataC-UUID' in data_manager.activated_data
    assert 'dataD-UUID' in data_manager.activated_data


def test_activate_with_super_id(data_manager):
    data_manager.activate('groupA-UUID')

    groupA_children_length = len(data_manager.id_map['groupA-UUID']['children'])
    groupB_children_length = len(data_manager.id_map['groupB-UUID']['children'])
    groupC_children_length = len(data_manager.id_map['groupC-UUID']['children'])
    activated_data_length = groupA_children_length + groupB_children_length + groupC_children_length
    assert activated_data_length == len(data_manager.activated_data)
    assert 'dataA-UUID' in data_manager.activated_data
    assert 'dataB-UUID' in data_manager.activated_data
    assert 'dataC-UUID' in data_manager.activated_data
    assert 'dataD-UUID' not in data_manager.activated_data


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


def test_add_group(data_manager):
    new_group_id = data_manager.add_group(None, 'root_group')
    assert new_group_id in data_manager.id_map
    found_new_group = False
    for child in data_manager.root['children']:
        if child['id'] == new_group_id:
            found_new_group = True
            break
    assert found_new_group


def test_add_data_request_with_name_rule(data_manager):
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


def test_add_data_request_url_params(data_manager):
    data = {
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
        'name': 'add_data_name'
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
    node_str = json.dumps(node)
    prop_str = json.dumps(prop)
    assert len(node_str) == len(prop_str)

{
  "snapshot": {
    "id": "c098559f-4d20-4aab-879d-ba63786c9553",
    "parent_id": None,
    "name": "imeituan://www.meituan.com/reviewlist",
    "type": "group",
    "super_id": None,
    "children": [
      {
        "id": "3106108a-15b7-45ba-add0-ccce1e1695e7",
        "parent_id": "c098559f-4d20-4aab-879d-ba63786c9553",
        "name": "/perf/prism-report-web",
        "type": "data"
      },
      {
        "id": "82d023ff-4098-493f-b082-a42b6efe62c8",
        "parent_id": "c098559f-4d20-4aab-879d-ba63786c9553",
        "name": "/perf/met_babel_android",
        "type": "data"
      },
      {
        "id": "1e5513c4-2476-445a-ae0c-850f1ccbd4bd",
        "parent_id": "c098559f-4d20-4aab-879d-ba63786c9553",
        "name": "debug-link",
        "type": "data"
      }
    ],
    "urlscheme": "imeituan://www.meituan.com/reviewlist?referid=635353299&refertype=1&source=101",
    "debug_link": "imeituan://www.meituan.com/travel/debugconfig?downloadjson=http://{{ip}}:{{port}}/mock/debug-link"
  },
  "events": [
    {
      "name": "/perf/prism-report-web",
      "request": {
        "headers": {
          "Content-Encoding": "gzip",
          "Accept-Charset": "UTF-8",
          "Mkoriginhost": "prism-report-fsp.dreport.meituan.net",
          "Mkoriginport": "443",
          "Mkscheme": "https",
          "Mktunneltype": "https",
          "Mkappid": "10",
          "Mkunionid": "000000000000045F61B21158D498590827317F3458233A161549945565238960",
          "Content-Type": "application/octet-stream",
          "Content-Length": "888",
          "Host": "172.30.43.166:9090",
          "Connection": "Keep-Alive",
          "Accept-Encoding": "gzip",
          "User-Agent": "okhttp/2.7.6"
        },
        "method": "POST",
        "query": {},
        "timestamp": 1635260532.749,
        "url": "https://prism-report-fsp.dreport.meituan.net/perf/prism-report-web?",
        "scheme": "https",
        "host": "prism-report-fsp.dreport.meituan.net",
        "port": "80",
        "path": "/perf/prism-report-web",
        "data": "eyJjYXRlZ29yeSI6InByaXNtLXJlcG9ydC1mc3AiLCJjYXRlZ29yeV90eXBlIjoiZmVfcGVyZiIsImVudiI6eyJhcHAiOiJjb20uc2Fua3VhaS5tZWl0dWFuIiwiZGV2aWNlVHlwZSI6IlBpeGVsIDRhIiwiaXNPaG9zIjpmYWxzZSwiYXBwVmVyc2lvbiI6IjExLjE0LjIwNCIsImJ1aWxkVmVyc2lvbiI6IjExLjE0LjIwNC4xNTA1MDIiLCJvcyI6IkFuZHJvaWQiLCJkZXZpY2VJZCI6IjAwMDAwMDAwMDAwMDA0NUY2MUIyMTE1OEQ0OTg1OTA4MjczMTdGMzQ1ODIzM0ExNjE1NDk5NDU1NjUyMzg5NjAiLCJ0b2tlbiI6IjU1NTA3YmI1Y2UwODg4MTgyNzkyMWI2YyIsImRldmljZVByb3ZpZGVyIjoiR29vZ2xlIiwibWNjbW5jIjoiIiwib3NWZXJzaW9uIjoiMTIiLCJzZGtWZXJzaW9uIjoiMy4xNC4xMyIsIm5ldHdvcmtUeXBlIjoiV0lGSee9kee7nCIsInJlcG9ydE5ldHdvcmtUeXBlIjoiV0lGSee9kee7nCIsInJlcG9ydFZlcnNpb24iOiIxMS4xNC4yMDQiLCJ0cyI6MTYzNTI2MDUzMjc2Nn0sImxvZ3MiOlt7InZhbHVlIjo0OTksInRzIjoxNjM1MjYwNTI5NzU3LCJ0YWdzIjp7InZpZXdTaXplIjoxMzYsImlzTWFpblRocmVhZCI6IjAiLCJsb2dVVUlkIjoiNTNkZTZhOGItNDQ2ZS00OWZhLWEzMTgtNWRjOWE5Zjk5MDdkIiwiRlNQRXhjZXB0aW9uIjowLCJjaXR5Ijoi5YyX5LqsIiwibHhfc2lkIjoiMzVkM2IyNWYtYWU5NS00YTRmLTgxOTEtOGMzMGIwMmQ0ZTY5MTYzNTI2MDUxNjAwMTM4MiIsIm5ld0ZzcFRpbWUiOjQ5OSwidGhyZWFkSWQiOiIxMTEiLCJvbkNyZWF0ZVRpbWUiOjE2MzUyNjA1MjQ4MzgsInJlYWNoQm90dG9tVGltZSI6MTYzNTI2MDUyNTMzNywiJGlkJCI6NSwicHJvY2Vzc05hbWUiOiJjb20uc2Fua3VhaS5tZWl0dWFuIiwibWF4TWVtQXBwIjoiNTM2ODcwOTEyIiwiY2FsY3VsYXRlVGltZSI6Mzc5MywiaXNGaXJzdExhdW5jaCI6dHJ1ZSwic2Vzc2lvbl91dWlkIjoiOWEyMTg0MWQtZDM3YS00MjY1LTk5NjYtOWJkODY1ZDZiYjQxIiwic3RhYmxlVGltZSI6MTYzNTI2MDUyNTMzNywiY2giOiJtZWl0dWFuaW50ZXJuYWx0ZXN0Iiwic2NoZW1lVXJsIjoiY29tLm1laXR1YW4uYW5kcm9pZC51Z2MucmV2aWV3Lmxpc3QudWkuUmV2aWV3TGlzdEFjdGl2aXR5Iiwic2Vzc2lvbl9pZCI6IjlhMjE4NDFkLWQzN2EtNDI2NS05OTY2LTliZDg2NWQ2YmI0MTE2MzUyNTE1Mjc3MTQ2NzUiLCJjcHVDb3JlTnVtcyI6OCwibWF4TWVtUGhvbmUiOiI1ODY1MjU5MDA4IiwiJHNhbXBsZV9yYXRlIjoxLCJ0aHJlYWROYW1lIjoiZnNwX2RldGVjdG9yIiwibWV0cmljc1Nka1ZlcnNpb24iOiIzLjE0LjE0IiwiJHMkIjoiZGRhYTMzMDItMTU1Yi00NzAwLThhYmUtODE2Mjk3YTFiZjZjIiwiY3B1TWF4RnJlcSI6IjIyMDgwMDAiLCIkc3RhdHVzIjoic3RhbmRhcmQiLCJkZXZpY2VMZXZlbCI6IlVOX0tOT1ciLCJzZXFfaWQiOjEyLCJ0cmlnZ2VyVHlwZSI6MCwiY3B1TWluRnJlcSI6IjMwMDAwMCIsImxvZ19zb3VyY2UiOjB9LCJ0eXBlIjoiRlNQIn0seyJ2YWx1ZSI6NDk5LCJ0cyI6MTYzNTI2MDUyOTc1NywidGFncyI6eyJ2aWV3U2l6ZSI6MTM2LCJpc01haW5UaHJlYWQiOiIwIiwibG9nVVVJZCI6IjUzZGU2YThiLTQ0NmUtNDlmYS1hMzE4LTVkYzlhOWY5OTA3ZCIsIkZTUEV4Y2VwdGlvbiI6MCwiY2l0eSI6IuWMl+S6rCIsImx4X3NpZCI6IjM1ZDNiMjVmLWFlOTUtNGE0Zi04MTkxLThjMzBiMDJkNGU2OTE2MzUyNjA1MTYwMDEzODIiLCJuZXdGc3BUaW1lIjo0OTksInRocmVhZElkIjoiMTExIiwib25DcmVhdGVUaW1lIjoxNjM1MjYwNTI0ODM4LCJyZWFjaEJvdHRvbVRpbWUiOjE2MzUyNjA1MjUzMzcsIiRpZCQiOjUsInByb2Nlc3NOYW1lIjoiY29tLnNhbmt1YWkubWVpdHVhbiIsIm1heE1lbUFwcCI6IjUzNjg3MDkxMiIsImNhbGN1bGF0ZVRpbWUiOjM3OTMsImlzRmlyc3RMYXVuY2giOnRydWUsInNlc3Npb25fdXVpZCI6IjlhMjE4NDFkLWQzN2EtNDI2NS05OTY2LTliZDg2NWQ2YmI0MSIsInN0YWJsZVRpbWUiOjE2MzUyNjA1MjUzMzcsImNoIjoibWVpdHVhbmludGVybmFsdGVzdCIsInNjaGVtZVVybCI6ImNvbS5tZWl0dWFuLmFuZHJvaWQudWdjLnJldmlldy5saXN0LnVpLlJldmlld0xpc3RBY3Rpdml0eSIsInNlc3Npb25faWQiOiI5YTIxODQxZC1kMzdhLTQyNjUtOTk2Ni05YmQ4NjVkNmJiNDExNjM1MjUxNTI3NzE0Njc1IiwiY3B1Q29yZU51bXMiOjgsIm1heE1lbVBob25lIjoiNTg2NTI1OTAwOCIsIiRzYW1wbGVfcmF0ZSI6MSwidGhyZWFkTmFtZSI6ImZzcF9kZXRlY3RvciIsIm1ldHJpY3NTZGtWZXJzaW9uIjoiMy4xNC4xNCIsIiRzJCI6ImRkYWEzMzAyLTE1NWItNDcwMC04YWJlLTgxNjI5N2ExYmY2YyIsImNwdU1heEZyZXEiOiIyMjA4MDAwIiwiJHN0YXR1cyI6InN0YW5kYXJkIiwiZGV2aWNlTGV2ZWwiOiJVTl9LTk9XIiwic2VxX2lkIjoxMiwidHJpZ2dlclR5cGUiOjAsImNwdU1pbkZyZXEiOiIzMDAwMDAiLCJsb2dfc291cmNlIjowfSwidHlwZSI6IlJlYWNoQm90dG9tRlNQIn1dfQ==\n"
      },
      "response": {
        "code": 200,
        "timestamp": 1635260532.819,
        "headers": {
          "lyrebird": "proxy",
          "Server": "Tengine",
          "Date": "Tue, 26 Oct 2021 15:02:12 GMT",
          "Content-Type": "application/octet-stream",
          "Content-Length": "2",
          "Connection": "keep-alive",
          "Expires": "Mon, 26 Oct 2020 15:02:12 GMT",
          "Cache-Control": "no-cache, private, no-cache, no-store, proxy-revalidate",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Credentials": "true"
        },
        "data": "T0s=\n"
      },
      "id": "3106108a-15b7-45ba-add0-ccce1e1695e7"
    },
    {
      "name": "/perf/met_babel_android",
      "request": {
        "headers": {
          "Content-Encoding": "gzip",
          "Accept-Charset": "UTF-8",
          "Mkoriginhost": "prism-report-fsp.dreport.meituan.net",
          "Mkoriginport": "443",
          "Mkscheme": "https",
          "Mktunneltype": "https",
          "Mkappid": "10",
          "Mkunionid": "000000000000045F61B21158D498590827317F3458233A161549945565238960",
          "Content-Type": "application/octet-stream",
          "Content-Length": "572",
          "Host": "172.30.43.166:9090",
          "Connection": "Keep-Alive",
          "Accept-Encoding": "gzip",
          "User-Agent": "okhttp/2.7.6"
        },
        "method": "POST",
        "query": {},
        "timestamp": 1635260529.264,
        "url": "https://prism-report-fsp.dreport.meituan.net/perf/met_babel_android?",
        "scheme": "https",
        "host": "prism-report-fsp.dreport.meituan.net",
        "port": "80",
        "path": "/perf/met_babel_android",
        "data": "eyJjYXRlZ29yeSI6ICJwcmlzbS1yZXBvcnQtZnNwIiwgImNhdGVnb3J5X3R5cGUiOiAiZmVfcGVyZiIsICJlbnYiOiB7ImFwcCI6ICJjb20uc2Fua3VhaS5tZWl0dWFuIiwgImRldmljZVR5cGUiOiAiUGl4ZWwgNGEiLCAiaXNPaG9zIjogZmFsc2UsICJhcHBWZXJzaW9uIjogIjExLjE0LjIwNCIsICJidWlsZFZlcnNpb24iOiAiMTEuMTQuMjA0LjE1MDUwMiIsICJvcyI6ICJBbmRyb2lkIiwgImRldmljZUlkIjogIjAwMDAwMDAwMDAwMDA0NUY2MUIyMTE1OEQ0OTg1OTA4MjczMTdGMzQ1ODIzM0ExNjE1NDk5NDU1NjUyMzg5NjAiLCAidG9rZW4iOiAiNTU1MDdiYjVjZTA4ODgxODI3OTIxYjZjIiwgImRldmljZVByb3ZpZGVyIjogIkdvb2dsZSIsICJtY2NtbmMiOiAiIiwgIm9zVmVyc2lvbiI6ICIxMiIsICJzZGtWZXJzaW9uIjogIjMuMTQuMTMiLCAibmV0d29ya1R5cGUiOiAiV0lGSVx1N2Y1MVx1N2VkYyIsICJyZXBvcnROZXR3b3JrVHlwZSI6ICJXSUZJXHU3ZjUxXHU3ZWRjIiwgInJlcG9ydFZlcnNpb24iOiAiMTEuMTQuMjA0IiwgInRzIjogMTYzNTI2MDUyOTI0Mn0sICJsb2dzIjogW3sidHMiOiAxNjM1MjYwNTI1OTY0LCAidGFncyI6IHsidGhyZWFkSWQiOiAiMiIsICJpc01haW5UaHJlYWQiOiAiMSIsICJsb2dVVUlkIjogIjllZTVlYTY5LWFlZjctNGZmYi1iYTU2LTMwYmUwNTM0M2ZlMCIsICIkaWQkIjogNSwgIiRzJCI6ICJkZGFhMzMwMi0xNTViLTQ3MDAtOGFiZS04MTYyOTdhMWJmNmMiLCAiY2l0eSI6ICJcdTUzMTdcdTRlYWMiLCAicHJvY2Vzc05hbWUiOiAiY29tLnNhbmt1YWkubWVpdHVhbiIsICJzY2hlbWVVcmwiOiAiY29tLm1laXR1YW4uYW5kcm9pZC51Z2MucmV2aWV3Lmxpc3QudWkuUmV2aWV3TGlzdEFjdGl2aXR5IiwgIiRzdGF0dXMiOiAic3RhbmRhcmQiLCAiZGV2aWNlTGV2ZWwiOiAiVU5fS05PVyIsICIkc2FtcGxlX3JhdGUiOiAxLCAidGhyZWFkTmFtZSI6ICJtYWluIiwgImxvZ19zb3VyY2UiOiAwfSwgInR5cGUiOiAiRlNQX1N0YXJ0In1dfQ==\n"
      },
      "response": {
        "code": 200,
        "timestamp": 1635260529.31,
        "headers": {
          "lyrebird": "proxy",
          "Server": "Tengine",
          "Date": "Tue, 26 Oct 2021 15:02:09 GMT",
          "Content-Type": "application/octet-stream",
          "Content-Length": "2",
          "Connection": "keep-alive",
          "Expires": "Mon, 26 Oct 2020 15:02:09 GMT",
          "Cache-Control": "no-cache, private, no-cache, no-store, proxy-revalidate",
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Credentials": "true"
        },
        "data": "T0s=\n"
      },
      "id": "82d023ff-4098-493f-b082-a42b6efe62c8"
    },
    {
      "name": "debug-link",
      "rule": {
        "request.url": "(?=.*debug-link)"
      },
      "request": {
        "method": "GET",
        "url": "debug-link",
        "headers": {}
      },
      "response": {
        "code": 200,
        "headers": {
          "Connection": "keep-alive",
          "Content-Type": "application/json;charset=utf-8"
        },
        "data": [
          {
            "type": "mock",
            "info": {
              "value": "http://{{ip}}:{{port}}/mock/"
            },
            "desc": "mock:The ip of mock serve"
          },
          {
            "type": "mockshark",
            "info": {
              "value": "http://{{ip}}:{{port}}/mock/"
            },
            "desc": "mockshark:The ip of mockshark serve"
          },
          {
            "type": "mockh5",
            "info": {
              "value": "http://{{ip}}:{{port}}/mock/"
            },
            "desc": "mockh5:The ip of mockh5 serve"
          },
          {
            "type": "mockbabel",
            "info": {
              "value": "http://{{ip}}:{{port}}/mock/"
            },
            "desc": "mockbabel:The ip of mockbabel serve"
          },
          {
            "type": "reportresult",
            "info": {
              "value": 1
            },
            "desc": "是否通过bable上报结果:1--上报结果 0--不上报结果"
          },
          {
            "type": "scheme",
            "info": {
              "value": "imeituan://www.meituan.com/reviewlist?referid=635353299&refertype=1&source=101"
            },
            "desc": "The scheme of target page"
          },
          {
            "type": "signin",
            "info": {
              "signin": 1,
              "countryCode": "86",
              "account": "188",
              "password": "jiulv"
            },
            "desc": "请保证此项的account和password正确且不为空. 登录,signin:登录标志(默认是true),countryCode:登录区号,account:登录账号,password:登录密码"
          }
        ]
      },
      "id": "1e5513c4-2476-445a-ae0c-850f1ccbd4bd"
    }
  ],
  "message": "URL: imeituan://www.meituan.com/reviewlist?referid=635353299&refertype=1&source=101\nContains 2 requests:\n1. https://prism-report-fsp.dreport.meituan.net/perf/prism-report-web\n2. https://prism-report-fsp.dreport.meituan.net/perf/met_babel_android",
  "channel": "snapshot",
  "id": "d20a7cd8-8636-4aee-aab3-bbba34befe8d",
  "timestamp": 1635260540.834,
  "sender": {
    "file": "publish_snapshot.py",
    "function": "publish_snapshot"
  }
}

events = {
    'snapshot': {
        'id': 'groupA-UUID',
        'parent_id': None,
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

def test_export_from_local(data_manager, tmpdir):

    def pop_id(node):
        if 'id' in node:
            node.pop('id')
        for child in node.get('children', []):
            pop_id(child)

    group_id, filename = data_manager.export_from_local(events)
    children = data_manager.get(group_id)['children']
    assert group_id in data_manager.id_map
    assert len(children) == len(events['events'])

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
            snapshot_data = events['snapshot']
            data_id = group_id
        else:
            snapshot_data = [e for e in events['events'] if e['name']==data['name']][0]
            data_id = data['id']

        file_set.add(data['id'])
        assert data == data_manager.get(data_id)
        assert data['id'] != snapshot_data['id']
        data_pop_id = pop_id(data)
        snapshot_data_pop_id = pop_id(snapshot_data)
        assert data_pop_id == snapshot_data_pop_id

    assert file_set == children_set

def test_export_from_remote(data_manager, tmpdir):
    def pop_id(node):
        if 'id' in node:
            node.pop('id')
        for child in node.get('children', []):
            pop_id(child)

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
            snapshot_data = events['snapshot']
            data_id = group_id
        else:
            snapshot_data = [e for e in events['events'] if e['name']==data['name']][0]
            data_id = data['id']

        file_set.add(data['id'])
        assert data == data_manager.get(data_id)
        assert data['id'] == snapshot_data['id']
        data_pop_id = pop_id(data)
        snapshot_data_pop_id = pop_id(snapshot_data)
        assert data_pop_id == snapshot_data_pop_id

    assert file_set == children_set


def test_import_from_local(data_manager):
    def pop_id(node):
        if 'id' in node:
            node.pop('id')
        for child in node.get('children', []):
            pop_id(child)

    group_id, filename = data_manager.export_from_local(events)
    children = data_manager.get(group_id)['children']
    assert group_id in data_manager.id_map
    assert len(children) == len(events['events'])


def test_import_from_file(data_manager, tmpdir):

    def pop_id(node):
        if 'id' in node:
            node.pop('id')
        for child in node.get('children', []):
            pop_id(child)

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

    group_pop_id = pop_id(group)
    new_group_pop_id = pop_id(new_group)
    assert group_pop_id == new_group_pop_id


def test_get_snapshot_file_detail(data_manager):
    group_id = 'groupB-UUID'
    filename = data_manager.export_from_remote(group_id)

    snapshot_info, output_path = data_manager.get_snapshot_file_detail(filename)
    assert snapshot_info == data_manager.id_map.get(group_id)
