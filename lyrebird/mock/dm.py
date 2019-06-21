import codecs
import json
import re
from pathlib import Path

PROP_FILE_NAME = '.lyrebird_prop'


class DataManager:
    def __init__(self):
        self.root_path: Path = None
        self.root = None
        self.id_map = {}
        self.activated_data = {}

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
        return self.id_map.get(_id)

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

    def add(self, parent_id, data):
        pass

    def delete(self, item_id):
        pass

    def cut(self, item_id):
        pass

    def copy(self, item_id):
        pass

    def paste(self, parent_id):
        pass

    """
    Conflict checker
    """

    def check_conflict(self):
        conflict_rules = []
        for data_id in self.activated_data:
            _data = self.activated_data[data_id]
            _rule = _data['rule']
            _hit_data = []
            for data_id in self.activated_data:
                _test_data = self.activated_data[data_id]
                if self._is_match_rule(_test_data, _rule):
                    _hit_data.append(_test_data)
            if len(_hit_data) > 1:
                conflict_rules.append({'data': _data, 'conflict_data': _hit_data})
        return conflict_rules


"""
Exceptions
"""


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
