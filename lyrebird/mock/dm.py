import codecs
import json
import os
import re
import uuid
from pathlib import Path
from urllib.parse import urlparse

PROP_FILE_NAME = '.lyrebird_prop'


class DataManager:
    def __init__(self):
        self.root_path: Path = None
        self.root = None
        self.id_map = {}
        self.activated_data = {}
        self.activated_group = {}
        self.clipboard = None
        self.save_to_group_id = None
        self.tmp_group = {'id': 'tmp_group', 'type': 'group', 'name': 'tmp-group', 'children': []}

    def set_root(self, root_path):
        """
        Set a new mock data root dir
        -----
        DataManager will reload all data from this new root dir.
        And all activited data will be removed from DataManager.
        """
        _root_path = Path(root_path)
        if not _root_path.exists():
            raise RootPathNotExists(root_path)
        if not _root_path.is_dir():
            raise RootPathIsNotDir(root_path)
        if not (_root_path / PROP_FILE_NAME).exists():
            raise LyrebirdPropNotExists((_root_path / PROP_FILE_NAME))
        self.root_path = _root_path
        self.reload()

    def reload(self):
        if not self.root_path:
            raise RootNotSet
        _root_prop_path = self.root_path / PROP_FILE_NAME
        with codecs.open(_root_prop_path) as f:
            _root_prop = json.load(f)
            self.root = _root_prop
            self.id_map = {}
            self._read_node(self.root)

    def _read_node(self, node):
        if 'id' in node:
            self.id_map[node['id']] = node
        if 'children' in node:
            for child in node['children']:
                self._read_node(child)

    def get(self, _id):
        """
        Get mock group or data by id
        """
        if not self.root:
            raise RootNotSet
        node = self.id_map.get(_id)
        if not node:
            raise IDNotFound(_id)
        if node.get('type') == 'group' or node.get('type') == None:
            return node
        elif node.get('type') == 'data':
            return self._load_data(_id)

    """
    Mock operations
    """

    def activate(self, _id):
        """
        Activite data by id
        """
        if not self.root:
            raise RootNotSet
        _node = self.get(_id)
        if _node:
            self._activate(_node)
        else:
            raise DataNotFound(f'ID:{_id}')
        self.activated_group[_id] = _node

    def _activate(self, node):
        if node.get('type', '') == 'data':
            _mock_data = self._load_data(node['id'])
            if _mock_data:
                self.activated_data[node['id']] = _mock_data
        elif node.get('type', '') == 'group':
            if 'children' in node:
                for child in node['children']:
                    self._activate(child)

    def _load_data(self, data_id):
        _data_file = self.root_path / data_id
        if not _data_file.exists():
            raise DataNotFound(f'Data file {_data_file}')
        with codecs.open(_data_file) as f:
            return json.load(f)

    def deactivate(self):
        """
        Clear activated data
        """
        self.activated_data = {}
        self.activated_group = {}

    def get_matched_data(self, flow):
        """
        Find matched mock data from activated data
        """
        _matched_data = []
        for _data_id in self.activated_data:
            _data = self.activated_data[_data_id]
            if self._is_match_rule(flow, _data.get('rule')):
                _matched_data.append(_data)
        return _matched_data

    def _is_match_rule(self, flow, rules):
        if not rules:
            return False
        for rule_key in rules:
            pattern = rules[rule_key]
            target = self._get_rule_target(rule_key, flow)
            if not re.search(pattern, target):
                return False
        return True

    def _get_rule_target(self, rule_key, flow):
        prop_keys = rule_key.split('.')
        result = flow
        for prop_key in prop_keys:
            result = result.get(prop_key)
            if not result:
                return None
        return result

    """
    Data tree operations
    """

    def _get_request_path(self, request):
        path = request.get('path')
        if not path:
            if not request.get('url'):
                return ''
            parsed_url = urlparse(request['url'])
            path = parsed_url.path
        return path

    def add_data(self, parent_id, data):
        if not isinstance(data, dict):
            raise DataObjectSouldBeADict
        if parent_id == 'tmp_group':
            parent_node = self.tmp_group
        else:
            parent_node = self.id_map.get(parent_id)
            if not parent_node:
                raise IDNotFound(parent_id)
            if parent_node['type'] == 'data':
                raise DataObjectCannotContainAnyOtherObject
        data_id = str(uuid.uuid4())
        data['id'] = data_id
        data['name'] = self._get_request_path(data['request'])
        data['rule'] = {
            'request.url': f'(?=.*{self._get_request_path(data["request"])})'
        }
        data_path = self.root_path / data_id
        with codecs.open(data_path, 'w') as f:
            # Save data file
            json.dump(data, f, ensure_ascii=False)
            # Update parent node
            # New data added in the head of child list
            parent_node['children'].insert(0, {
                'id': data_id,
                'name': data.get('name', self._get_request_path(data["request"])),
                'type': 'data',
                'parent_id': parent_id
            })
            # Update ID mapping
            self.id_map[data_id] = data
        self._save_prop()
        return data_id

    def add_group(self, parent_id, name):
        if parent_id == None:
            parent_node = self.root
        else:
            parent_node = self.id_map.get(parent_id)
        if not parent_node:
            raise IDNotFound(parent_id)
        if parent_node.get('type') == 'data':
            raise DataObjectCannotContainAnyOtherObject
        # Add group
        group_id = str(uuid.uuid4())
        new_group = {
            'id': group_id,
            'name': name,
            'type': 'group',
            'parent_id': parent_id,
            'children': []
        }
        # New group added in the head of child list
        parent_node['children'].insert(0, new_group)
        # Register ID
        self.id_map[group_id] = new_group
        # Save prop
        self._save_prop()
        return group_id

    def delete(self, _id):
        self._delete(_id)
        # Save prop
        self._save_prop()

    def _delete(self, _id):
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
        # Delete children
        if 'children' in target_node and len(target_node['children']) > 0:
            for child in target_node['children']:
                self._delete(child['id'])
        # Delete from ID mapping
        self.id_map.pop(_id)
        # Delete from file system
        if target_node['type'] == 'data':
            data_file_path = self.root_path / _id
            os.remove(data_file_path)

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

    def paste(self, parent_id):
        if not self.clipboard:
            raise NoneClipbord
        _parent_node = self.id_map.get(parent_id)
        _node = self.clipboard['node']
        if not _parent_node:
            raise IDNotFound(parent_id)
        if self.clipboard['type'] == 'cut':
            _origin_parent = self.id_map.get(_node['parent_id'])
            _origin_parent['children'].remove(_node)
            _parent_node['children'].append(_node)
            _node['parent_id'] = parent_id
        elif self.clipboard['type'] == 'copy':
            self._copy_node(_parent_node, _node)
        self._save_prop()

    def _copy_node(self, target_node, node):
        new_node = {}
        new_node.update(node)
        new_node['id'] = str(uuid.uuid4())
        new_node['parent_id'] = target_node['id']
        # Add to target node
        target_node['children'].append(new_node)
        # Register ID
        self.id_map[new_node['id']] = new_node
        if new_node['type'] == 'group':
            new_node['children'] = []
            for child in node['children']:
                self._copy_node(new_node, child)
        elif new_node['type'] == 'data':
            self._copy_file(node)

    def _copy_file(self, data_node):
        _id = data_node['id']
        origin_file_path = self.root_path / _id
        new_file_id = str(uuid.uuid4())
        new_file_path = self.root_path / new_file_id
        with codecs.open(origin_file_path, 'r') as inputfile, codecs.open(new_file_path, 'w') as outputfile:
            origin_text = inputfile.read()
            prop = json.loads(origin_text)
            prop['id'] = new_file_id
            new_prop_text = json.dumps(prop, ensure_ascii=False)
            outputfile.write(new_prop_text)

    def _save_prop(self):
        # Save prop
        prop_file = self.root_path / PROP_FILE_NAME
        with codecs.open(prop_file, 'w') as f:
            json.dump(self.root, f, ensure_ascii=False)

    """
    Conflict checker
    """

    def check_conflict(self, _id):
        node = self.id_map.get(_id)
        if not node:
            raise IDNotFound(_id)
        data_array = []

        def _read_data(node):
            if node.get('type') == 'data':
                _data_file = self.root_path / node['id']
                with codecs.open(_data_file, 'r') as f:
                    _data = json.load(f)
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

    def _get_abs_parent_path(self, node, path=''):
        if 'parent_id' not in node:
            return path
        parent_node = self.id_map.get(node['parent_id'])
        if not parent_node:
            return path
        current_path = '/' + node['name'] + path
        return self._get_abs_parent_path(parent_node, path=current_path)
    """
    Record API
    """

    def save_data(self, data):
        if len(self.activated_group) > 0:
            # TODO use self.save_to_group_id
            target_group_id = list(self.activated_group.keys())[0]
            self.add_data(target_group_id, data)
        else:
            self.add_data('tmp_group', data)

    """
    Editor
    """

    def update_group(self, _id, data):
        ignore_keys = ['id', 'parent_id', 'type', 'children']
        update_data = {k: data[k] for k in data if k not in ignore_keys}
        node = self.id_map.get(_id)
        if not node:
            raise IDNotFound(_id)
        node.update(update_data)
        self._save_prop()

    def update_data(self, _id, data):
        node = self.id_map.get(_id)
        if not node:
            raise IDNotFound(_id)
        node['name'] = data['name']

        data_file = self.root_path / _id
        if not data_file.exists():
            raise DataNotFound(_id)
        with codecs.open(data_file, 'w') as f:
            data_str = json.dumps(data, ensure_ascii=False)
            f.write(data_str)
        self._save_prop()


# -----------------
# Exceptions
# -----------------

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


class DataObjectCannotContainAnyOtherObject(Exception):
    pass


class DataObjectSouldBeADict(Exception):
    pass


class IDNotFound(Exception):
    pass


class NoneClipbord(Exception):
    pass
