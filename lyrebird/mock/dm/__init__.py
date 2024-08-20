import math
import uuid
import json
import time
import codecs
from copy import deepcopy
import shutil
import traceback
from pathlib import Path
from urllib.parse import urlparse
from collections import OrderedDict
from lyrebird import utils, application
from lyrebird.log import get_logger
from lyrebird.utils import RedisDict
from lyrebird.application import config
from lyrebird.mock import context
from lyrebird.mock.dm.match import MatchRules
from lyrebird.mock.dm.temp_mock import TempMock
from lyrebird.config import CONFIG_TREE_SHOW_CONFIG

PROP_FILE_NAME = '.lyrebird_prop'
logger = get_logger()


class DataManager:

    def __init__(self):
        self.root_path: Path = None
        self.display_data_map = {}
        self.id_map = {}
        self.activated_data = OrderedDict()
        self.activated_group = {}
        self.is_activated_data_rules_contains_request_data = False
        self.LEVEL_SUPER_ACTIVATED = 3
        self.clipboard = None
        self._adapter = None

        self.snapshot_import_cache = {}
        self.SNAPSHOT_SUFFIX = '.lb'
        self.COPY_NODE_NAME_SUFFIX = ' - copy'
        self.root = self.get_default_root()
        self._snapshot_workspace = None

        self.add_group_ignore_keys = set(['id', 'type', 'children'])
        self.update_group_ignore_keys = set(['id', 'parent_id', 'type', 'children'])
        self.supported_data_type = self.get_supported_data_type()
        self.virtual_node_data_type = set(['config']) # TODO Next is `super``

        self.virtual_base_config_id = None

        self.unsave_keys = set()

        self.DELETE_STEP = 100
        self.is_deleting_lock = False

        # init temp mock
        self.temp_mock_tree = TempMock()

        self.tree = []
        self.open_nodes = []

        if config.get('enable_multiprocess', False):
            try:
                self.async_activate_group = RedisDict(host=config.get('redis_host', '127.0.0.1'),
                                                    port=config.get('redis_port', 6379),
                                                    db=config.get('redis_db', 0))
                self.activate = dm_asyncio_activate_decorator(self, self.activate)
                self.deactivate = dm_asyncio_activate_decorator(self, self.deactivate)
            except Exception as e:
                config['enable_multiprocess'] = False
                logger.error(f'Start enable multiprocess failed, Redis connection error: {e}')

    @property
    def snapshot_workspace(self):
        if not self._snapshot_workspace:
            self._snapshot_workspace = Path(application._cm.ROOT) / 'snapshot'
        if not self._snapshot_workspace.exists():
            self._snapshot_workspace.mkdir()
        return self._snapshot_workspace

    @snapshot_workspace.setter
    def snapshot_workspace(self, workspace):
        self._snapshot_workspace = workspace

    def get_supported_data_type(self):
        supported_data_type = ['data', 'json']
        if application.config.get(CONFIG_TREE_SHOW_CONFIG):
            supported_data_type.append('config')
        return supported_data_type

    def get_default_root(self):
        return {
            'id': str(uuid.uuid4()),
            'name': '$',
            'type': 'group',
            'parent_id': None,
            'label': [],
            'children': []
        }

    def set_adapter(self, adapter_cls):
        # TODO: Load overridden function only
        self._adapter = adapter_cls(self)

    def set_root(self, uri):
        self._adapter._set_root(uri)

    def reload(self):
        self._adapter._reload()
        self.handle_node_type_config()
        self.add_parent()
        self.add_super_by()

    def get_open_nodes(self):
        return self.open_nodes

    def add_open_node(self, id):
        if id not in self.open_nodes:
            self.open_nodes.append(id)

    def save_open_nodes(self, data):
        self.open_nodes = list(set(data))

    def get_tree(self):
        return self.tree
    
    def save_tree(self, data):
        self.root = data

    def _get_group_children(self, group_id):
        children = self._adapter._get_group_children(group_id)
        parent_node = self.id_map.get(group_id)
        if not parent_node:
            logger.error('IDNotFound, id=' + group_id)
            return []
        self.handle_group_config(children, parent_node['id'])

        for child in children:
            # update id_map
            if child['id'] not in self.id_map:
                self.id_map.update({
                    child['id']: child
                })

            self.add_parent_generator(child, parent_node)
            self.add_super_by(node=child)

        children.sort(key=lambda sub_node: sub_node['name'])
        return children

    def init_config_base_node(self):
        if self.virtual_base_config_id:
            return

        root_id = self.root['id']
        root_node = self.id_map.get(root_id)
        if not root_node:
            return

        root_children = root_node.get('children', [])
        for node in root_children:
            if node['type'] == 'config':
                self.virtual_base_config_id = node['id']
                return

    def handle_node_type_config(self):
        self.init_config_base_node()
        if not self.virtual_base_config_id:
            return

        all_new_config_node = {}
        for id_, node in self.id_map.items():
            if node['type'] != 'group':
                continue

            if 'children' not in node:
                node['children'] = []

            new_config_node = self.handle_group_config(node['children'], id_)
            if not new_config_node:
                continue

            all_new_config_node.update(new_config_node)

        if all_new_config_node:
            self.id_map.update(all_new_config_node)

    def handle_group_config(self, node_list, node_id):
        has_config_index = -1
        for index, node in enumerate(node_list):
            if node['type'] == 'config':
                has_config_index = index
                break

        is_show_config = application.config.get(CONFIG_TREE_SHOW_CONFIG)
        has_config = has_config_index != -1
        if is_show_config == has_config:
            return

        elif has_config and not is_show_config:
            del node_list[has_config_index]
            return

        elif is_show_config and not has_config:
            if not self.virtual_base_config_id:
                return
            new_config_node = {}

            config_node_id = str(uuid.uuid4())
            config_node = {
                'id': config_node_id,
                'name': '.Settings',
                'type': 'config',
                'parent_id': node_id,
                'link': self.virtual_base_config_id
            }
            node_list.append(config_node)
            new_config_node[config_node_id] = config_node

            return new_config_node

    def add_parent(self, node=None):
        if not node:
            root_id = self.root['id']
            root = self.id_map.get(root_id)
            self.add_parent_generator(root)
        else:
            parent_node = self.id_map.get(node['parent_id'])
            self.add_parent_generator(node, parent_node=parent_node)
        self.unsave_keys.update(['parent', 'abs_parent_path'])

    def add_parent_generator(self, node, parent_node=None):
        parent_node_parent = parent_node['parent'] if parent_node and parent_node.get('parent') else []
        parent_obj = parent_node_parent + [{
            'id': node['id'],
            'name': node['name'],
            'type': node['type'],
            'parent_id': node['parent_id']
        }]

        abs_parent_path = f"{parent_node['abs_parent_path']}{node['name']}/" if parent_node and parent_node.get('abs_parent_path') else '/'

        node.update({
            'parent': parent_obj,
            'abs_parent_path': abs_parent_path
        })

        if not node.get('children'):
            return

        for child in node['children']:
            self.add_parent_generator(child, node)

    def add_super_by(self, node=None):
        node_list = [node] if node else self.id_map.values()

        for node in node_list:
            if not node.get('super_id'):
                continue
            super_parent_node = self.id_map.get(node['super_id'])
            if not super_parent_node:
                continue
            if not super_parent_node.get('super_by'):
                super_parent_node['super_by'] = []
            super_parent_node['super_by'].append({
                'id': node['id'],
                'name': node['name']
            })
        self.unsave_keys.add('super_by')

    def get_group(self, _id):
        return self.get(_id)
    
    def get_data(self, _id):
        return self.get(_id)

    def get(self, _id):
        """
        Get mock group or data by id
        """
        if not self.root:
            raise RootNotSet
        node = self.id_map.get(_id)
        if not node:
            raise IDNotFound(_id)

        link = node.get('link')
        if link:
            link_node = self.id_map.get(_id)
            if not link_node:
                logger.error('link node not found!')
                raise IDNotFound(link_node)
            data = self.get(node['link'])
            data['link'] = data['id']
            data['id'] = link_node['id']
            return data

        if node.get('type') == 'group' or node.get('type') == None:
            return self._adapter._get_group(_id)
        elif node.get('type') == 'data':
            return self._adapter._load_data(_id)
        elif node.get('type') == 'json':
            return self._adapter._load_data(_id)
        elif node.get('type') == 'config':
            data = self._adapter._load_data(_id)
            data.pop('type', None)
            data.pop('name', None)
            return data
        else:
            raise UnsupportedType

    def is_data_virtual_node(self, node):
        if node['type'] == 'config':
            if 'link' in node:
                return node['link'] == self.virtual_base_config_id
 
        return False

    # -----
    # Mock operations
    # -----

    def make_data_map_by_group(self, group_ids):
        self.display_data_map = {k:v for k,v in self.root.items() if k!='children'}
        self.display_data_map['children'] = []

        for group_id in group_ids:
            map_pointer = self.display_data_map['children']

            group = self.id_map.get(group_id)
            group_abs_parent_obj = self._get_abs_parent_obj(group)

            # init parent
            # the last node in group['abs_parent_path'] is node itself, expand node itself
            # expand root which is already in the data_map
            for group_info in group_abs_parent_obj[1:-1]:
                parent_id = group_info['id']

                for index, child in enumerate(map_pointer):
                    if parent_id == child['id']:
                        map_pointer = map_pointer[index]['children']
                        break

                else:
                    node = self.id_map.get(parent_id)

                    new_node = {k:v for k,v in node.items() if k != 'children'}
                    new_node['children'] = []
                    map_pointer.append(new_node)
                    # Because of new_node is `append` into map_pointer, new_node is the last child of map_pointer
                    # move map_pointer first, sort after
                    map_pointer = map_pointer[-1]['children']
                    map_pointer.sort(key=lambda x:x.get('name', ''))

            # update node and node's children
            node = self.id_map.get(group_id)
            map_pointer.append(node)

        self._sort_tree_children_by_name(self.display_data_map)

        return self.display_data_map

    def root_without_children(self):
        async_tree = {k: v for k,v in self.root.items() if k not in ['children']}
        async_tree['children'] = []
        return async_tree

    def activate(self, search_id, **kwargs):
        """
        Activite data by id
        """
        if not self.root:
            raise RootNotSet
        _node = self._adapter._get_activate_group(search_id)
        if not _node:
            raise IDNotFound(f'ID:{search_id}')

        _id = _node['id']
        node_id_list = self._collect_activate_node(_node, level_lefted=self.LEVEL_SUPER_ACTIVATED)

        ordered_data_id = []
        for node_id in node_id_list:
            activated_node = self.id_map.get(node_id)
            ordered_data_id += self._collect_data_in_node(activated_node)
        data_list = self._adapter._load_data_by_query({'id': ordered_data_id})

        # Only one group could be activated and reactived
        # Deactivate all activated group before activate
        self.deactivate()

        data_map = {d['id']: d for d in data_list}
        self.activated_data.update({i: data_map[i] for i in ordered_data_id if data_map.get(i)})
        self.activated_group[_id] = _node

        # Apply config
        config = self._get_activated_data_config()
        if config:
            application._cm.add_config(config, type='dm', level=-1, apply_now=True)

        # After activate
        self._check_activated_data_rules_contains_request_data()
        self._adapter._after_activate(**kwargs)

    def _check_activated_data_rules_contains_request_data(self):
        self.is_activated_data_rules_contains_request_data = False
        for _data_id in self.activated_data:
            _data = self.activated_data[_data_id]
            rules = _data.get('rule')
            if not rules:
                continue
            for rule_key in rules.keys():
                if rule_key.startswith('request.data'):
                    self.is_activated_data_rules_contains_request_data = True
                    return 

    def _collect_activate_node(self, node, level_lefted=1):
        id_list = [node['id']]
        if level_lefted <= 0:
            return id_list
        if not node.get('super_id'):
            return id_list
        if node.get('super_id') == node['id']:
            raise SuperIdCannotBeNodeItself(node['id'])

        _super_id = node.get('super_id')
        _super_node = self.id_map.get(_super_id)
        if not _super_node:
            raise IDNotFound(f'Super node ID: {_super_id}')

        id_list.extend(self._collect_activate_node(_super_node, level_lefted=level_lefted-1))
        return id_list

    def _collect_data_in_node(self, node):
        id_list = []
        if self.is_data_virtual_node(node):
            return []
        if node.get('type') in self.supported_data_type:
            return [node['id']]
        elif node.get('type', '') == 'group':
            if 'children' in node:
                for child in node['children']:
                    id_list.extend(self._collect_data_in_node(child))
        return id_list

    def _collect_node(self, node, target_type=None):
        id_list = []
        if self.is_data_virtual_node(node):
            return []

        node_type = node.get('type')
        if not target_type or node_type in target_type:
            id_list.append(node['id'])

        if node_type == 'group':
            if 'children' in node:
                for child in node['children']:
                    id_list.extend(self._collect_node(child, target_type=target_type))

        return id_list

    def deactivate(self):
        """
        Clear activated data
        """
        config = self._get_activated_data_config()
        if config:
            application._cm.remove_config(config, type='dm', apply_now=True)

        self.activated_data = OrderedDict()
        self.activated_group = {}
        self._check_activated_data_rules_contains_request_data()

    def reactive(self):
        for _group_id in self.activated_group:
            self.activate(_group_id)
            context.application.socket_io.emit('activatedGroupUpdate')

    def get_matched_data_multiple_source(self, flow):
        matched_data = self.temp_mock_tree.get_matched_data(flow)
        if matched_data:
            return {
                'data': matched_data,
                'parent': self.temp_mock_tree.root
            }

        matched_data = self.get_matched_data(flow)
        if matched_data:
            return {
                'data': matched_data,
                'parent': list(self.activated_group.values())[0]
            }

    def get_matched_data(self, flow):
        """
        Find matched mock data from activated data
        """
        if self.is_activated_data_rules_contains_request_data:
            decode_flow = {}
            application.encoders_decoders.decoder_handler(flow, output=decode_flow)
        else:
            decode_flow = flow
        _matched_data = []
        for _data_id in self.activated_data:
            _data = self.activated_data[_data_id]
            if self._is_match_rule(decode_flow, _data.get('rule')):
                _matched_data.append(deepcopy(_data))
                break

        for response_data in _matched_data:
            if 'response' not in response_data:
                continue
            if 'data' not in response_data['response']:
                continue
            if not response_data['response']['data']:
                continue
            self._format_respose_data(response_data)

        return _matched_data

    @staticmethod
    def _format_respose_data(flow):
        # TODO render mock data before response, support more functions
        origin_response_data = flow['response']['data']

        try:
            flow['response']['data'] = utils.render(flow['response']['data'])
        except Exception:
            flow['response']['data'] = origin_response_data
            logger.warning(f'Format response data error! {flow["request"]["url"]}\n {traceback.format_exc()}')

    def _is_match_rule(self, flow, rules):
        return MatchRules.match(flow, rules)

    def _get_activated_data_config(self):
        config_id = None
        for id_, data in self.activated_data.items():
            if 'json' not in data:
                continue

            node = self.id_map.get(id_)
            if not node:
                continue
            if node['type'] == 'config':
                config_id = id_
                break

        if not config_id:
            return
        config_node = self.activated_data.get(config_id)
        if not config_node:
            return

        try:
            return json.loads(config_node['json'])
        except Exception:
            logger.error(f'Load config {config_node["id"]} error! \n {traceback.format_exc()}')

    # -----
    # Data tree operations
    # -----

    def _get_request_path(self, request):
        path = request.get('path')
        if not path:
            if not request.get('url'):
                return ''
            parsed_url = urlparse(request['url'])
            path = parsed_url.path
        return path

    def _make_data(self, raw_data, **kwargs):
        data = dict(raw_data)
        _data_id = kwargs.get('data_id') or str(uuid.uuid4())
        data['id'] = _data_id

        if data.get('type') == 'json':
            self._make_data_json(raw_data, data)
        elif data.get('type') == 'config':
            self._make_data_config(raw_data, data)
        elif data.get('type') == 'data':
            self._make_data_http_data(raw_data, data)
        else:
            self._make_data_http_data(raw_data, data)

        return data

    def _make_data_http_data(self, raw_data, data):
        if 'request' in data:
            # TODO remove it with inspector frontend
            data['request'] = dict(raw_data['request'])

            _data_name = data['name'] if data.get('name') else self._get_data_name(data)
            _data_rule = data['rule'] if data.get('rule') else self._adapter._get_data_rule(data['request'])
            if 'data' in data['request']:
                data['request']['data'] = utils.flow_data_2_str(data['request']['data'])
        else:
            _data_name = data.get('name')
            _data_rule = {'request.url': '(?=.*YOUR-REQUEST-PATH)(?=.*PARAMS)'}
            data['request'] = {}

        if 'response' in data:
            # TODO remove it with inspector frontend
            data['response'] = dict(raw_data['response'])

            if 'data' in data['response']:
                data['response']['data'] = utils.flow_data_2_str(data['response']['data'])
        else:
            data['response'] = {}

        # proxy_response will not be saved
        if 'proxy_response' in data:
            del data['proxy_response']

        data['name'] = _data_name
        data['rule'] = _data_rule

    def _get_data_name(self, data):
        name = 'New Data'
        request = data.get('request')
        if not request:
            return name

        url = request.get('url')
        if not url:
            return name

        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        path = parsed_url.path
        if path:
            name = path
        elif hostname:
            name = hostname
        else:
            name = url[0:100]

        return name

    def _make_data_json(self, raw_data, data):
        if 'json' not in data:
            data['json'] = {}

        data['name'] = data['name'] if data.get('name') else 'Unnamed JSON'

    def _make_data_config(self, raw_data, data):
        if 'json' not in data:
            data['json'] = {}

        data['name'] = '.Settings'

    def add_data(self, parent_id, raw_data, **kwargs):
        if not isinstance(raw_data, dict):
            raise DataObjectShouldBeADict

        if not raw_data.get('type'):
            raw_data['type'] = 'data'

        if raw_data['type'] not in self.supported_data_type:
            raise UnsupportedType

        parent_node = None
        parent_node = self.id_map.get(parent_id)
        if not parent_node:
            raise IDNotFound(parent_id)
        if parent_node['type'] != 'group':
            raise OnlyGroupCanContainAnyOtherObject

        data = self._make_data(raw_data, **kwargs)
        data['parent_id'] = parent_id
        _data_id = data['id']
        _data_name = data.get('name')

        output_path = (kwargs['output'] / _data_id) if kwargs.get('output') else None

        self._adapter._add_data(data, path=output_path)

        if parent_node:
            data_node = {}
            data_node['id'] = _data_id
            data_node['name'] = _data_name
            data_node['type'] = data.get('type')
            data_node['parent_id'] = parent_id

            # New data added in the head of child list
            parent_node['children'].insert(0, data_node)
            logger.debug(f'*** Add to node {data_node}')
            # Update ID mapping
            self.id_map[_data_id] = data_node
            self._adapter._add_group(data_node)

        return _data_id

    def add_group(self, data):
        ignore_key = self.add_group_ignore_keys | self.unsave_keys
        new_group = {k: data[k] for k in data if k not in ignore_key}

        parent_id = data.get('parent_id')
        if parent_id == None:
            parent_node = self.root
        else:
            parent_node = self.id_map.get(parent_id)

        if not parent_node:
            raise IDNotFound(parent_id)
        if parent_node.get('type') == 'data':
            raise OnlyGroupCanContainAnyOtherObject

        # Add group
        group_id = str(uuid.uuid4())
        new_group.update({
            'id': group_id,
            'type': 'group',
            'children': []
        })
        # New group added in the head of child list
        if 'children' not in parent_node:
            parent_node['children'] = []
        parent_node['children'].insert(0, new_group)
        # Register ID
        self.id_map[group_id] = new_group
        # Save prop
        self._adapter._add_group(new_group)
        # Update tree
        if parent_node['id'] in self.open_nodes:
            parent_children = self._get_group_children(parent_node['id'])
            tree_target_node = self.get_target_node(self.tree, parent_node['id'])
            if not tree_target_node:
                tree_target_node = {}
                tree_target_node['children'] = parent_children
        return group_id

    def add_group_by_path(self, path):
        parent_name = path.strip('/')
        current = self.root
        if not parent_name:
            return current['id']
        parent_name_list = parent_name.split('/')
        for name in parent_name_list:
            for child in current['children']:
                if name == child['name']:
                    current = child
                    break
            else:
                group_id = self.add_group({
                    'name': name,
                    'parent_id': current['id']
                })
                current = self.id_map.get(group_id)
        return current['id']

    def delete(self, _id):
        target_node = self.id_map.get(_id)
        if not target_node:
            raise IDNotFound(_id)
        parent_id = target_node.get('parent_id')
        # Remove refs
        if parent_id:
            parent = self.id_map.get(parent_id)
            parent['children'].remove(target_node)
        else:
            self.root['children'].remove(target_node)
        self._delete(_id)

    def _delete(self, _id):
        target_node = self.id_map.get(_id)
        if not target_node:
            raise IDNotFound(_id)
        if 'children' in target_node and len(target_node['children']) > 0:
            for child in target_node['children'][::-1]:
                self._delete(child['id'])
                target_node['children'].pop(-1)
        # Remove from activated_group
        if _id in self.activated_group:
            self.activated_group.pop(_id)
        # Delete from ID mapping
        self.id_map.pop(_id)
        # Delete from mock tree
        self._adapter._delete_group(_id)
        # Delete from file system
        if target_node['type'] == 'data':
            self._adapter._delete_data(_id)

    def cut(self, _id):
        _node = self.id_map.get(_id)
        if not _node:
            raise IDNotFound(_id)
        self.clipboard = {
            'type': 'cut',
            'id': _id,
            'node': _node
        }

    def copy(self, _id):
        _node = self.id_map.get(_id)
        if not _node:
            raise IDNotFound(_id)
        self.clipboard = {
            'type': 'copy',
            'id': _id,
            'node': _node
        }

    def import_(self, node, json=None, path=None):
        self.clipboard = {
            'type': 'import',
            'id': node['id'],
            'node': node,
            'json': json,
            'path': path
        }

    def paste(self, parent_id, **kwargs):
        if not self.clipboard:
            raise NoneClipbord
        _parent_node = self.id_map.get(parent_id)
        _node = self.clipboard['node']
        if not _parent_node:
            raise IDNotFound(parent_id)
        if not _parent_node.get('children'):
            _parent_node['children'] = []
        if self.clipboard['type'] == 'cut':
            _origin_parent = self.id_map.get(_node['parent_id'])
            _origin_parent['children'].remove(_node)
            _parent_node['children'].insert(0, _node)
            _node['parent_id'] = parent_id
            _group_id = _node['id']
            self._adapter._update_group(_node)
        elif self.clipboard['type'] == 'copy':
            new_name = self._get_copy_node_new_name(_node)
            _group_id = self._copy_node(_parent_node, _node, name=new_name, origin_name=_node['name'], **kwargs)
        elif self.clipboard['type'] == 'import':
            _group_id = self._copy_node(_parent_node, _node, **kwargs)
        return _group_id

    def duplicate(self, _id, **kwargs):
        return self._adapter.duplicate(_id)

    def _copy_node(self, parent_node, node, **kwargs):
        if self.is_data_virtual_node(node):
            return

        new_node = {}
        new_node.update(node)
        new_node['id'] = str(uuid.uuid4())
        new_node['parent_id'] = parent_node['id']
        new_node['name'] = kwargs['name'] if kwargs.get('name') else new_node['name']
        # Add to target node
        if not parent_node.get('children'):
            parent_node['children'] = []
        parent_node['children'].insert(0, new_node)
        # Add node
        self._adapter._add_group(new_node, **kwargs)
        # Register ID
        self.id_map[new_node['id']] = new_node
        if new_node['type'] == 'group':
            kwargs.pop('name') if kwargs.get('name') else None
            kwargs.pop('origin_name') if kwargs.get('origin_name') else None
            new_node['children'] = []
            for child in node['children']:
                self._copy_node(new_node, child, **kwargs)
        elif new_node['type'] == 'data':
            self._copy_data(new_node, node, **kwargs)
        elif new_node['type'] == 'json':
            self._copy_data(new_node, node, **kwargs)
        return new_node['id']

    def _copy_data(self, new_data_node, data_node, **kwargs):
        _id = data_node['id']

        if self.clipboard.get('json'):
            event = self.clipboard.get('json', {}).get(_id)
            if not event:
                raise DataNotFound
            prop = {k:v for k,v in event.items()}
        elif self.clipboard.get('path'):
            with codecs.open(Path(self.clipboard['path'])/_id) as f:
                prop = json.load(f)
        else:
            prop = self._adapter._load_data(_id)

        prop['id'] = new_data_node['id']
        prop['name'] = kwargs.pop('name') if kwargs.get('name') else prop['name']
        self._adapter._add_data(prop)

    def _get_copy_node_new_name(self, _node):
        return _node['name'] + self.COPY_NODE_NAME_SUFFIX

    def _sort_children_by_name(self):
        for node_id in self.id_map:
            node = self.id_map[node_id]
            if 'children' not in node:
                # fix mock data group has no children
                if node['type'] == 'group':
                    node['children'] = []
                continue
            node['children'] = sorted(node['children'], key=lambda sub_node: sub_node['name'])

    def _sort_tree_children_by_name(self, node):
        if not node.get('children'):
            return
        node['children'].sort(key=lambda sub_node: sub_node['name'])
        for child in node['children']:
            self._sort_tree_children_by_name(child)

    # -----
    # Conflict checker
    # -----

    def check_conflict(self, _id):
        node = self.id_map.get(_id)
        if not node:
            raise IDNotFound(_id)
        data_array = []

        def _read_data(node):
            if node.get('type') == 'data':
                _data = self._adapter._load_data(node['id'])
                _data['parent_id'] = node['parent_id']
                data_array.append(_data)
            elif node.get('type') == 'group':
                for child in node['children']:
                    _read_data(child)
        _read_data(node)
        return self.check_conflict_data(data_array)

    def activated_data_check_conflict(self):
        data_array = list(self.activated_data.values())
        return self.check_conflict_data(data_array)

    def check_conflict_data(self, data_array):
        conflict_rules = []
        for _data in data_array:
            _rule = _data['rule']
            _hit_data = []
            for _test_data in data_array:
                if self._is_match_rule(_test_data, _rule):
                    _target_node = {
                        'id': _test_data['id'],
                        'name': _test_data['name'],
                        'url': _test_data['request']['url'],
                        'abs_parent_path': self._get_abs_parent_path(_test_data)
                    }
                    _hit_data.append(_target_node)
            if len(_hit_data) > 1:
                _src_node = {
                    'id': _data['id'],
                    'name': _data['name'],
                    'rule': _data['rule'],
                    'abs_parent_path': self._get_abs_parent_path(_data)
                }
                conflict_rules.append(
                    {
                        'data': _src_node,
                        'conflict_data': _hit_data
                    }
                )
        return conflict_rules

    # TODO: delete
    def _get_abs_parent_path(self, node, path='/'):
        parent_node = self._get_node_parent(node)
        if parent_node is None:
            return path
        current_path = '/' + node['name'] + path
        return self._get_abs_parent_path(parent_node, path=current_path)

    def _get_abs_parent_obj(self, node, parent_obj=None):
        if parent_obj is None:
            parent_obj = []
        if 'id' not in node:
            return parent_obj
        node_info = self.id_map.get(node['id'])
        if not node_info:
            return parent_obj
        parent_obj.insert(0, {
            'id': node_info['id'],
            'name': node_info['name'],
            'type': node_info['type'],
            'parent_id': node_info['parent_id']
        })
        parent_node = self._get_node_parent(node)
        if parent_node is None:
            return parent_obj
        return self._get_abs_parent_obj(parent_node, parent_obj=parent_obj)

    def _get_node_parent(self, node):
        if 'parent_id' not in node:
            return None
        parent_node = self.id_map.get(node['parent_id'])
        if not parent_node:
            return None
        return parent_node

    # -----
    # Record API
    # -----

    def save_data(self, data):
        if len(self.activated_group) == 0:
            raise ActivateGroupNotFound

        target_group_id = list(self.activated_group.keys())[0]
        self.add_data(target_group_id, data)

    # -----
    # Editor
    # -----

    def update_group(self, _id, data, save=True, **kwargs):
        node = self.id_map.get(_id)
        if not node:
            raise IDNotFound(_id)

        old_name = node['name'] if node['name'] != data['name'] else ''
        # Remove unsave_key add by DataManager itself
        for key in self.unsave_keys:
            data.pop(key) if key in data else None

        # Uneditable key
        for key in self.update_group_ignore_keys:
            data[key] = node.get(key)

        # labels are ordered, sorted by label name
        if 'label' not in data:
            data['label'] = []
        elif 'label' in data and isinstance(data['label'], list):
            data['label'].sort(key=lambda x:x.get('name', '').lower())

        message = self._adapter._update_group(data, **kwargs) if save else None

        # Update node
        # 1. Add new key into node
        update_data = {k: data[k] for k in data if k not in self.update_group_ignore_keys}
        node.update(update_data)

        # 2. Remove deleted key in node
        delete_keys = [k for k in node if k not in data and k not in self.update_group_ignore_keys and k not in self.unsave_keys]
        for key in delete_keys:
            node.pop(key)

        # 3. Update existed value
        # 3. Modify abs_parent_path、parent、children
        if old_name:
            self.update_node_when_name_changed(node, _id, data['name'], old_name)

        # 4. Update tree
        tree_target_node = self.get_target_node(self.tree, _id)
        if tree_target_node:
            tree_target_node.update(update_data)
            for key in delete_keys:
                tree_target_node.pop(key)
            if old_name:
                self.update_node_when_name_changed(tree_target_node, _id, data['name'], old_name)
            if not message.get('message', None):
                message['message'] = tree_target_node

        return message

    def get_target_node(self, tree, id):
        if not tree:
            return
        for node in tree:
            if node['id'] not in self.open_nodes:
                continue
            if node['id'] == id:
                return node
            result = self.get_target_node(node.get('children', []), id)
            if result is not None:
                return result                

    def update_node_when_name_changed(self, node, id, new_name, old_name):
        abs_parent_path = node.get('abs_parent_path', '')
        parts = abs_parent_path.rsplit(old_name, 1)
        if len(parts) > 1:
            abs_parent_path = new_name.join(parts)
        node['abs_parent_path'] = abs_parent_path

        for parent in node.get('parent', []):
            if (parent['id'] == id):
                parent['name'] = new_name
        
        for child in node.get('children', []):
            self.update_node_when_name_changed(child, id, new_name, old_name)

    def update_data(self, _id, data):
        node = self.id_map.get(_id)
        if not node:
            raise IDNotFound(_id)

        if node.get('link'):
            data['type'] = node['type']
            self.add_data(node['parent_id'], data, data_id=data['id'])
            return

        tree_target_node = None
        if 'name' in data and node['name'] != data['name']:
            self.update_node_when_name_changed(node, _id, data['name'], node['name'])
            tree_target_node = self.get_target_node(self.tree, _id)
            if tree_target_node:
                tree_target_node['name'] = data['name']
                self.update_node_when_name_changed(tree_target_node, _id, data['name'], node['name'])
            node['name'] = data['name']
        self._adapter._update_data(data)
        self._adapter._update_group(node)
        return tree_target_node or node

    # -----
    # Snapshot
    # -----

    def export_from_local(self, event):
        group_id = self.import_from_local(event)
        filename = self.export_from_remote(group_id)
        return group_id, filename

    def export_from_remote(self, node_id):
        snapshot_path = self._get_snapshot_path()
        node = self.id_map.get(node_id)
        self._write_file(snapshot_path/PROP_FILE_NAME, node)

        ordered_data_id = self._collect_data_in_node(node)
        data_list = self._adapter._load_data_by_query({'id': ordered_data_id})
        for mock_data in data_list:
            self._write_file(snapshot_path/mock_data['id'], mock_data)

        filename = utils.compress_tar(snapshot_path, snapshot_path, suffix=self.SNAPSHOT_SUFFIX)
        self._remove_file([snapshot_path])
        return filename

    def import_from_local(self, event):
        _prop = event['snapshot']
        parent_path = config.get('snapshot.import.workspace', '/')
        parent_id = self.add_group_by_path(parent_path)

        new_data_map = {}
        for e in event['events']:
            data = self._make_data(e, data_id=e['id'])
            new_data_map[e['id']] = data

        self.import_(_prop, json=new_data_map)
        return self.paste(parent_id)

    def import_from_file(self, parent_id, input_path, **kwargs):
        snapshot_info, output_path = self.get_snapshot_file_detail(input_path)
        if kwargs.get('name'):
            snapshot_info['name'] = kwargs['name']

        self.import_(snapshot_info, path=output_path)
        _group_id = self.paste(parent_id=parent_id, path=output_path)
        self._remove_file([input_path, output_path])
        return _group_id

    def read_snapshot_from_link(self, link):
        snapshot_path = self._get_snapshot_path()
        snapshot_filename = Path(f'{snapshot_path}{self.SNAPSHOT_SUFFIX}')

        utils.download(link, snapshot_filename)
        return snapshot_filename

    def get_snapshot_file_detail(self, input_path):
        try:
            output_path = utils.decompress_tar(input_path)
        except Exception as e:
            raise LyrebirdSnapshotBroken(e)

        snapshot_prop = output_path / PROP_FILE_NAME

        if not snapshot_prop.exists():
            raise LyrebirdPropNotExists
        with codecs.open(str(snapshot_prop)) as f:
            snapshot_info = json.load(f)
        return snapshot_info, output_path

    def _write_file(self, path, data):
        data_str = json.dumps(data, ensure_ascii=False)
        with codecs.open(path, 'w') as f:
            f.write(data_str)

    def _remove_file(self, files):
        for filepath in files:
            path = Path(filepath)
            if path.is_dir() and path.exists():
                shutil.rmtree(path)
            elif path.is_file() and path.exists():
                path.unlink()

    def _get_snapshot_path(self):
        temp_dir_name = f"{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}-{str(uuid.uuid4())}"
        snapshot_path = self.snapshot_workspace / temp_dir_name
        snapshot_path.mkdir()
        return snapshot_path

    def _get_type_hashmap(self, ids):
        type_map = {
            'group': [],
            'data': [],
            'json': [],
            'config': []
        }
        for id_ in ids:
            node = self.id_map.get(id_)
            if not node:
                continue
            node_type = node['type']
            if node_type not in type_map:
                continue
            type_map[node_type].append(id_)
        return type_map

    def _delete_remove_from_parent(self, id_):
        target_node = self.id_map.get(id_)
        if not target_node:
            return
        parent_id = target_node.get('parent_id')
        if not parent_id:
            return
        parent = self.id_map.get(parent_id)
        if not parent:
            return
        parent['children'].remove(target_node)

    # batch action
    def delete_by_query(self, query):
        node_delete_group_ids = query.get('groups', [])
        node_delete_data_ids = query.get('data', [])
        all_id_list = list(set(node_delete_group_ids + node_delete_data_ids))

        times = math.ceil(len(all_id_list) / self.DELETE_STEP)
        for index in range(times):
            start_point = index * self.DELETE_STEP
            stop_point = (index + 1) * self.DELETE_STEP
            id_list = all_id_list[start_point : stop_point]

            context.application.socket_io.emit('statusBarProcess', {
                'message': f'DataManager deleting ({start_point}/{len(all_id_list)})',
                'state': 'process'
            })


            for id_ in id_list:
                # Delete from parent
                self._delete_remove_from_parent(id_)

                # Remove from activated_group
                if id_ in self.activated_group:
                    self.activated_group.pop(id_)

                # Delete from ID mapping
                self.id_map.pop(id_)

            # Modify tree
            for id_ in node_delete_group_ids:
                if id_ in self.open_nodes:
                    self.open_nodes.remove(id_)
            
            def delete_subtrees(tree, ids_to_delete):
                new_tree = []
                for node in tree:
                    if node['id'] not in ids_to_delete:
                        node['children'] = delete_subtrees(node.get('children', []), ids_to_delete)
                        new_tree.append(node)
                return new_tree

            self.tree = delete_subtrees(self.tree, id_list)

            # Delete
            self._adapter._delete_group_by_query({'id': node_delete_group_ids})
            self._adapter._delete_data_by_query({'id': node_delete_data_ids})

        context.application.socket_io.emit('statusBarProcess', {
            'message': f'DataManager delete finish! ({len(all_id_list)}/{len(all_id_list)})',
            'state': 'finish'
        })

    def update_by_query(self, query, data):
        return self.update_group(data.get('id'), data, query=query)


class DataManagerV2(DataManager):
    def __init__(self):
        super().__init__()
        self.activate_config = {}

    def reload(self, reset=False, open_nodes=[]):
        if reset:
            self.reset()
        if not open_nodes:
            if not self.open_nodes:
                open_nodes = [self._adapter.root_id]
            else:
                open_nodes = self.open_nodes
        self._adapter._reload(open_nodes)

        if not self.open_nodes:
            self.open_nodes = [self._adapter.root_id]
        self.reactive()
        return self.root

    def set_root(self, uri):
        self._adapter._set_root(uri)
        if self._adapter.root_id:
            self.open_nodes = [self._adapter.root_id]

    def reset(self):
        self.open_nodes = [self._adapter.root_id]
        self.deactivate()

    def _get_group_children(self, group_id):
        result = self._adapter._get_group_children(group_id)
        self.handle_group_config(result, group_id)
        self.add_open_node(group_id)
        return result

    def handle_group_config(self, node_list, node_id):
        has_config_index = -1
        for index, node in enumerate(node_list):
            if node['type'] == 'config':
                has_config_index = index
                break

        is_show_config = application.config.get(CONFIG_TREE_SHOW_CONFIG)
        has_config = has_config_index != -1
        if has_config and not is_show_config:
            del node_list[has_config_index]
            return

    def get_group(self, _id):
        return self._adapter._load_group(_id)

    def get_data(self, _id):
        return self._adapter._load_data(_id)
    
    def add_group(self, data):
        return self._adapter._add_group(data)
    
    def update_group(self, _id, data, save=True, **kwargs):
        if not data:
            raise ValueError("No data to update")
        data['id'] = _id
        result = self._adapter._update_group(data, **kwargs)
        if _id in self.activated_group:
            self.reactive()
        return result if save else None
    
    def delete(self, _id):
        return self._adapter._delete(_id)
    
    def delete_by_query(self, query):
        data_id_list = query.get('data', [])
        group_id_list = query.get('groups', [])
        all_id_list = data_id_list + group_id_list
        context.application.socket_io.emit('statusBarProcess', {
            'message': 'DataManager deleting...',
            'state': 'process'
        })
        self._adapter._batch_delete(query)
        context.application.socket_io.emit('statusBarProcess', {
            'message': f'DataManager delete finish! ({len(all_id_list)}/{len(all_id_list)})',
            'state': 'finish'
        })
        # Remove from activated_group
        for id_ in all_id_list:
            if id_ in self.activated_data.keys():
                self.activated_data.pop(id_)
            if id_ in self.activated_group:
                self.activated_group.pop(id_)
            if id_ in self.open_nodes:
                self.open_nodes.remove(id_)

    def update_data(self, _id, data):
        self._adapter._update_data(_id, data)

    def add_data(self, parent_id, raw_data, **kwargs):
        if not isinstance(raw_data, dict):
            raise DataObjectShouldBeADict

        if not raw_data.get('type'):
            raw_data['type'] = 'data'
        if raw_data['type'] not in self.supported_data_type:
            raise UnsupportedType
        data = self._make_data(raw_data, **kwargs)
        _data_id = data['id']
        output_path = (kwargs['output'] / _data_id) if kwargs.get('output') else None
        self._adapter._add_data(data, path=output_path, type='data', parent_id=parent_id)
        return _data_id

    """
    Search API
    """
    def search(self, search_str, sender=None):
        return self._adapter._search(search_str, sender)

    """
    activate/deavtivate
    """
    def activate(self, search_id, **kwargs):
        """
        Activite data by id
        """
        activate_info = self._adapter._activate(search_id)
        config = activate_info.get('config', {}).get('json', {})
        flows = activate_info.get('flows', [])
        group_info = activate_info.get('groupInfo', {})
        # TODO: 兼容V1，增加children字段
        group_info['children'] = self._adapter._get_group_children(group_info.get('id'))
        logger.info(f'Activate {len(flows)} flows ,load config {activate_info.get("config", {}).get("id")}')

        # Only one group could be activated and reactived
        # Deactivate all activated group before activate
        self.deactivate()
        data_map = {}
        for flow in flows:
            data_map[flow['id']] = flow
        self.activated_data.update(data_map)
        self.activated_group[search_id] = group_info
        # Apply config
        if config:
            try:
                self.activate_config = json.loads(config)
            except Exception as e:
                logger.error('Failed to parse the config, the config did not take effect!')
            application._cm.add_config(self.activate_config, type='dm', level=-1, apply_now=True)
        # TODO:After activate
        self._check_activated_data_rules_contains_request_data()
        self._adapter._after_activate(activated_group = group_info, activated_data = self.activated_data, **kwargs)

    def deactivate(self):
        """
        Clear activated data
        """
        if self.activate_config:
            application._cm.remove_config(self.activate_config, type='dm', apply_now=True)
        self.activate_config = {}
        self.activated_data = OrderedDict()
        self.activated_group = {}
        self._check_activated_data_rules_contains_request_data()

    """
    cut/copy/paste
    """
    def cut(self, _id):
        self.clipboard = {
            'type': 'cut',
            'id': _id,
        }

    def copy(self, _id):
        self.clipboard = {
            'type': 'copy',
            'id': _id,
        }

    def paste(self, parent_id, **kwargs):
        if not self.clipboard:
            raise NoneClipbord
        self.clipboard['parent_id'] = parent_id
        result = self._adapter._paste(self.clipboard, **kwargs)
        self._adapter._reload(self.open_nodes)
        return result
    
    def duplicate(self, _id, **kwargs):
        return {
            'message': 'The duplicate function has been deprecated！',
            'id': None
        }
    
    def export_from_remote(self, node_id):
        snapshot_path = self._get_snapshot_path() 
        result = self._adapter._get_node_prop(node_id) # 导出节点信息
        if result is None:
            raise ValueError
        self._write_file(snapshot_path/PROP_FILE_NAME, result.get('prop'))
        data_list = self._adapter._load_data_by_query({'id': result.get('childDataIds')})
        for mock_data in data_list:
            self._write_file(snapshot_path/mock_data['id'], mock_data)

        filename = utils.compress_tar(snapshot_path, snapshot_path, suffix=self.SNAPSHOT_SUFFIX)
        self._remove_file([snapshot_path])
        return filename
    
    # -----
    # Conflict checker
    # -----

    def check_conflict(self, _id):
        data_array = self._adapter._read_data(_id)
        return self.check_conflict_data(data_array)

    # -----
    # Record API
    # -----
    def save_data(self, data):
        super().save_data(data)
        self.reload()


# -----------------
# decorator
# -----------------

def dm_asyncio_activate_decorator(self, func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        self.async_activate_group.clear()
        self.async_activate_group.update(self.activated_group)
        return result
    return wrapper

# -----------------
# Exceptions
# -----------------

class DumpPropError(Exception):
    pass


class ActivateGroupNotFound(Exception):
    pass


class RootNotSet(Exception):
    pass


class RootPathNotExists(Exception):
    pass


class RootPathIsNotDir(Exception):
    pass


class LyrebirdPropNotExists(Exception):
    pass


class DataNotFound(Exception):
    pass


class OnlyGroupCanContainAnyOtherObject(Exception):
    pass


class UnsupportedType(Exception):
    pass


class SuperIdCannotBeNodeItself(Exception):
    pass


class DataObjectShouldBeADict(Exception):
    pass


class IDNotFound(Exception):
    pass


class BaseConfigNodeNotFound(Exception):
    pass


class NoneClipbord(Exception):
    pass


class NonePropFile(Exception):
    pass


class TooMuchPropFile(Exception):
    pass


class NodeExist(Exception):
    pass


class LyrebirdSnapshotBroken(Exception):
    pass
