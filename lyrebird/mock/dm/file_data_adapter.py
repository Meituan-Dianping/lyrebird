import os
import json
import shutil
import codecs
from pathlib import Path


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

    def _add_group(self, data, **kwargs):
        self._save_prop()

    def _update_group(self, data):
        self._save_prop()

    def _delete_group(self, data):
        self._save_prop()

    # data
    def _load_data(self, data_id, path=None):
        if not path:
            path = self.context.root_path / data_id
        if not Path(path).exists():
            raise DataNotFound(f'Data file {path}')
        with codecs.open(path) as f:
            return json.load(f)

    def _add_data(self, data, path=None):
        if not path:
            path = self.context.root_path / data['id']
            self._add_group(data)
        self._save_data(path, data)

    def _delete_data(self, _id):
        data_file_path = self.context.root_path / _id
        os.remove(data_file_path)

    def _update_data(self, data):
        self._save_data(self.context.root_path/data['id'], data)

    def _save_prop(self):
        # TODO: Handle frequent writes
        self.context._sort_children_by_name()
        prop_str = PropWriter().parse(self.context.root)
        prop_file = self.context.root_path / PROP_FILE_NAME
        with codecs.open(prop_file, 'w') as f:
            f.write(prop_str)
        self.context.reactive()

    def _save_data(self, path, data):
        prop_str = json.dumps(data, ensure_ascii=False)
        with codecs.open(path, 'w') as f:
            f.write(prop_str)

    # snapshot
    def _write_prop_to_custom_path(self, outfile_path, node):
        self._add_data(node, path=outfile_path/PROP_FILE_NAME)

    def _write_file_to_custom_path(self, outfile_path, file_content):
        self.add_data(None, file_content, data_id=file_content['id'], output=outfile_path)

    def decompress_snapshot(self):
        snapshot_path = self.context.snapshot_helper.get_snapshot_path()
        self.context.snapshot_helper.save_compressed_file(snapshot_path)
        self.context.snapshot_helper.decompress_snapshot(f'{snapshot_path}.lb', f'{snapshot_path}')
        if not Path(f'{snapshot_path}/{PROP_FILE_NAME}').exists():
            raise LyrebirdPropNotExists
        _prop = self._load_data(None, path=f'{snapshot_path}/{PROP_FILE_NAME}')
        return {'snapshot_detail': _prop, 'snapshot_storage_path': f'{snapshot_path}'}

    def import_snapshot(self, parent_id, snapshot_name, path=None):
        snapshot_info = self.decompress_snapshot()
        snapshot_info['snapshot_detail']['name'] = snapshot_name
        self.context.import_(node=snapshot_info['snapshot_detail'])
        _group_id = self.context.paste(parent_id=parent_id, custom_input_file_path=snapshot_info['snapshot_storage_path'])
        tmp_snapshot_file_list = [
            snapshot_info['snapshot_storage_path'],
            f'{snapshot_info["snapshot_storage_path"]}.lb'
        ]
        if path:
            tmp_snapshot_file_list.append(path)
        self.remove_tmp_snapshot_file(tmp_snapshot_file_list)
        return _group_id

    def export_snapshot_from_event(self, event_json):
        snapshot_path = self.context.snapshot_helper.get_snapshot_path()
        if not event_json.get('snapshot') or not event_json.get('events'):
            raise SnapshotEventNotInCorrectFormat
        _prop = event_json.get('snapshot')
        self._write_prop_to_custom_path(snapshot_path, _prop)
        for mock_data in event_json.get('events'):
            self._write_file_to_custom_path(snapshot_path, mock_data)
        self.context.snapshot_helper.compress_snapshot(snapshot_path, snapshot_path)
        self.remove_tmp_snapshot_file([snapshot_path])
        return f'{snapshot_path}.lb'

    def export_snapshot_from_dm(self, node_id):
        snapshot_path = self.context.snapshot_helper.get_snapshot_path()
        _prop = self.context.id_map.get(node_id)
        self._write_prop_to_custom_path(snapshot_path, _prop)
        data_id_map = {}
        self.context.snapshot_helper.get_data_id_map(_prop, data_id_map)
        for mock_data_id in data_id_map:
            shutil.copy(self.context.root_path / mock_data_id, snapshot_path / mock_data_id)
        self.context.snapshot_helper.compress_snapshot(snapshot_path, snapshot_path)
        return f'{snapshot_path}.lb'

    def remove_tmp_snapshot_file(self, files):
        for filepath in files:
            path = Path(filepath)
            if path.is_dir() and path.exists():
                shutil.rmtree(path)
            elif path.is_file() and path.exists():
                path.unlink()

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


class IDNotFound(Exception):
    pass


class DataNotFound(Exception):
    pass


class DumpPropError(Exception):
    pass


class RootPathIsNotDir(Exception):
    pass


class LyrebirdPropNotExists(Exception):
    pass


class SnapshotEventNotInCorrectFormat(Exception):
    pass


data_adapter = FileDataAdapter
