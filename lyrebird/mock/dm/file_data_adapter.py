import os
import json
import codecs
from pathlib import Path
from ..dm import DataManager

PROP_FILE_NAME = '.lyrebird_prop'


class FileDataAdapter:

    def __init__(self, context_self):
        self.context = context_self

    def _set_root(self, root_path):
        """
        Set a new mock data root dir
        -----
        DataManager will reload all data from this new root dir.
        And all activited data will be removed from DataManager.
        """
        _root_path = Path(root_path).expanduser()
        if not _root_path.exists():
            _root_path.mkdir(parents=True, exist_ok=True)
        if not _root_path.is_dir():
            raise RootPathIsNotDir(root_path)
        _root_path.mkdir(parents=True, exist_ok=True)
        self.context.root_path = _root_path
        self._reload()

    def _reload(self):
        self.context.id_map = {}
        self._load_prop()
        self.context._sort_children_by_name()

    def _load_prop(self):
        path = self.context.root_path / PROP_FILE_NAME
        if not path.exists():
            self._save_prop()
        with codecs.open(path) as f:
            _root_prop = json.load(f)
        self.context.root = _root_prop
        self._init_id_map(self.context.root)

    def _init_id_map(self, node):
        if 'id' in node:
            self.context.id_map[node['id']] = node
        if 'children' in node:
            for child in node['children']:
                self._init_id_map(child)

    def _add_group(self, data):
        self._save_prop()

    def _update_group(self, data):
        self._save_prop()

    def _delete_group(self, data):
        self._save_prop()

    # data
    def _load_data(self, data_id, path=None):
        if not path:
            path = self.context.root_path / data_id
        if not path.exists():
            raise DataNotFound(f'Data file {path}')
        with codecs.open(path) as f:
            return json.load(f)

    def _add_data(self, data, path=None):
        if not path:
            path = self.context.root_path / data['id']
        self.context._save_data(path, data)

    def _delete_data(self, _id):
        data_file_path = self.context.root_path / _id
        os.remove(data_file_path)

    def _update_data(self, data):
        self.context._save_data(self.context.root_path/data['id'], data)

    def _save_prop(self):
        self.context._sort_children_by_name()
        prop_str = PropWriter().parse(self.context.root)
        # Save prop
        prop_file = self.context.root_path / PROP_FILE_NAME
        with codecs.open(prop_file, 'w') as f: # 
            f.write(prop_str)
        # Reactive mock data
        _activated_group = self.context.activated_group
        self.context.deactivate()
        for _group_id in _activated_group:
            self.context.activate(_group_id)

    def _save_data(self, path, data):
        prop_str = json.dumps(data)
        with codecs.open(path, 'w') as f:
            f.write(prop_str)


class PropWriter:

    def __init__(self):
        self.indent = 0
        self.parsers = {
            'dict': self.dict_parser,
            'list': self.list_parser,
            'int': self.int_parser,
            'str': self.str_parser,
            'bool': self.bool_parser,
            'NoneType': self.none_parser
        }

    def parse(self, prop):
        prop_type = type(prop)
        parser = self.parsers.get(prop_type.__name__)
        if not parser:
            raise DumpPropError(f'Not support type {prop_type}')
        return parser(prop)

    def dict_parser(self, val):
        dict_str = '{'
        children = None
        for k, v in val.items():
            if k == 'children':
                children = v
                continue
            dict_str += f'"{k}":{self.parse(v)},'
        if children is not None:
            dict_str += self.children_parser(children)
        if dict_str.endswith(','):
            dict_str = dict_str[:-1]
        dict_str += '}'
        return dict_str

    def list_parser(self, val):
        list_str = '['
        for item in val:
            item_str = self.parse(item)
            list_str += item_str + ','
        if list_str.endswith(','):
            list_str = list_str[:-1]
        list_str += ']'
        return list_str

    def int_parser(self, val):
        return f'{val}'

    def str_parser(self, val):
        return json.dumps(val, ensure_ascii=False)

    def bool_parser(self, val):
        return json.dumps(val)

    def none_parser(self, val):
        return 'null'

    def children_parser(self, val):
        self.indent += 1
        children_str = '"children":['
        for child in val:
            child_str = self.parse(child)
            children_str += '\n' + '  '*self.indent + child_str + ','
        if children_str.endswith(','):
            children_str = children_str[:-1]
        children_str += ']'
        self.indent -= 1
        return children_str


class DataNotFound(Exception):
    pass


class DumpPropError(Exception):
    pass


class RootPathIsNotDir(Exception):
    pass


dataAdapter = FileDataAdapter
