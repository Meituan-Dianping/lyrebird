import os
import json
import codecs
from pathlib import Path
from urllib.parse import urlparse


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
        self.context.root_path = _root_path
        self.context.reload()

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

    def _get_group(self, id_):
        return self.context.id_map.get(id_)

    def _add_group(self, data, **kwargs):
        self._save_prop()

    def _update_group(self, data):
        self._save_prop()

    def _delete_group(self, data):
        self._save_prop()

    def _delete_group_by_query(self, query):
        self._save_prop()

    # data
    def _load_data(self, data_id, path=None):
        if not path:
            path = self.context.root_path / data_id
        if not Path(path).exists():
            raise DataNotFound(f'Data file {path}')
        with codecs.open(path) as f:
            return json.load(f)

    def _load_data_by_query(self, query):
        datas = []
        for _id in query.get('id', []):
            datas.append(self._load_data(_id))
        return datas

    def _add_data(self, data, path=None):
        if not path:
            path = self.context.root_path / data['id']
            self._add_group(data)
        self._save_data(path, data)

    def _delete_data(self, _id):
        data_file_path = self.context.root_path / _id
        os.remove(data_file_path)

    def _delete_data_by_query(self, query):
        for _id in query.get('id', []):
            self._delete_data(_id)

    def _update_data(self, data):
        self._save_data(self.context.root_path/data['id'], data)

    def _save_prop(self):
        # TODO: Handle frequent writes
        self.context._sort_children_by_name()
        prop_writer = PropWriter()
        prop_writer.dict_ignore_key.update(self.context.unsave_keys)

        prop_str = prop_writer.parse(self.context.root)
        prop_file = self.context.root_path / PROP_FILE_NAME
        with codecs.open(prop_file, 'w') as f:
            f.write(prop_str)
        self.context.reactive()

    def _save_data(self, path, data):
        prop_str = json.dumps(data, ensure_ascii=False)
        with codecs.open(path, 'w') as f:
            f.write(prop_str)

    def _get_data_name(self, data):
        name = 'New Data'
        request = data.get('request')
        if not request:
            return name

        url = request.get('url')
        if not url:
            return name

        parsed_url = urlparse(url)
        host = parsed_url.hostname
        path = parsed_url.path
        if path:
            name = path
        elif host:
            name = host
        else:
            name = url[0:100]

        return name

    def _get_data_rule(self, request):
        pattern = 'YOUR-REQUEST-PATH'
        url = request.get('url')
        if not url:
            return {'request.url': f'(?=.*{pattern})'}

        parsed_url = urlparse(url)
        host = parsed_url.netloc
        path = parsed_url.path
        query = parsed_url.query
        if path and host:
            pattern = path
            if query:
                pattern += '\?' 
            elif url.endswith(path):
                pattern += '$'

        elif host:
            pattern = host
            if url.endswith(host):
                pattern += '$'

        else:
            pattern = url
        return {'request.url': f'(?=.*{pattern})'}

    def _get_activate_group(self, search_id):
        return self.context.id_map.get(search_id)

    def _after_activate(self, **kwargs):
        pass

    # duplicate
    def duplicate(self, _id):
        self.context.copy(_id)
        _node = self.context.id_map.get(_id)
        if not _node:
            raise IDNotFound(_id)
        parent_id = _node.get('parent_id')
        if not parent_id:
            raise IDNotFound(parent_id)

        origin_name = _node.get('name')

        new_uuid = self.context.paste(parent_id)
        duplicate_node = self.context.id_map.get(new_uuid)
        duplicate_node_name = duplicate_node.get('name')
        return {
            'message': f'Duplicat group {origin_name} success! new group name: {duplicate_node_name}',
            'id': new_uuid
        }


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
        self.dict_ignore_key = set()

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
            if k in self.dict_ignore_key:
                continue
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


class IDNotFound(Exception):
    pass


class DataNotFound(Exception):
    pass


class DumpPropError(Exception):
    pass


class RootPathIsNotDir(Exception):
    pass


data_adapter = FileDataAdapter
