import os
import json
import codecs
from ..dm import DataManager

PROP_FILE_NAME = '.lyrebird_prop'


class FileDataAdapter(DataManager):
    def reload(self):
        path = self.root_path / PROP_FILE_NAME
        if not path.exists():
            self._save_prop()
        with codecs.open(path) as f:
            _root_prop = json.load(f)

        self.root = _root_prop
        self.id_map = {}
        self._read_node(self.root)
        self._sort_children_by_name()

    def _add_group(self, data):
        self._save_prop()

    def _delete_group(self, data, category):
        self._save_prop()

    def _delete_data(self, _id):
        data_file_path = self.root_path / _id
        os.remove(data_file_path)

    def _update_group(self, data):
        self._save_prop()

    def _save_prop(self):
        self._sort_children_by_name()
        prop_str = PropWriter().parse(self.root)
        # Save prop
        prop_file = self.root_path / PROP_FILE_NAME
        with codecs.open(prop_file, 'w') as f: # 
            f.write(prop_str)
        # Reactive mock data
        _activated_group = self.activated_group
        self.deactivate()
        for _group_id in _activated_group:
            self.activate(_group_id)

    # data
    def _load_data(self, data_id, path=None):
        if not path:
            path = self.root_path / data_id
        if not path.exists():
            raise DataNotFound(f'Data file {path}')
        with codecs.open(path) as f:
            return json.load(f)

    def _add_data(self, data, path=None):
        if not path:
            path = self.root_path / data['id']
        self._save_data(path, data)

    def _delete_data(self, _id):
        p = self.root_path/_id
        os.remove(p)

    def _update_data(self, data):
        self._save_data(self.root_path/data['id'], data)

    def _save_data(self, path, data):
        prop_str = json.dumps(data)
        with codecs.open(path, 'w') as f:
            f.write(prop_str)
            # json.dump(data, f, ensure_ascii=False)


    def _sort_children_by_name(self):
        for node_id in self.id_map:
            node = self.id_map[node_id]
            if 'children' not in node:
                # fix mock data group has no children
                if node['type'] == 'group':
                    node['children'] = []
                continue
            node['children'] = sorted(node['children'], key=lambda sub_node: sub_node['name'])



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