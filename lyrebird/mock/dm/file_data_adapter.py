import os
import json
import codecs
from pathlib import Path
from urllib.parse import urlparse
from lyrebird.log import get_logger
import uuid
import traceback
from copy import deepcopy


logger = get_logger()


PROP_FILE_NAME = '.lyrebird_prop'


class FileDataAdapter:

    def __init__(self, context_self):
        self.context = context_self
        
        self.root_path: Path = None
        self.display_data_map = {}
        self.LEVEL_SUPER_ACTIVATED = 3

        self.COPY_NODE_NAME_SUFFIX = ' - copy'
        self.root_id = None

        self.add_group_ignore_keys = set(['id', 'type', 'children'])
        self.update_group_ignore_keys = set(['id', 'parent_id', 'type', 'children'])
        self.supported_data_type = ['data', 'json', 'config']
        self.virtual_node_data_type = set(['config']) # TODO Next is `super``
        self.virtual_base_config_id = None

        self.unsave_keys = set()

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
        self.root_path = _root_path
        self._reload()

    def _reload(self, open_nodes=[]):
        self.context.id_map = {}
        self._load_prop()
        self._sort_children_by_name()
        self.add_parent()
        self.add_super_by()
        self.root_id = self.context.root['id']

    def _load_prop(self):
        path = self.root_path / PROP_FILE_NAME
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

    def _get_tree(self):
        return self.context.root

    def _get_group(self, id_):
        return self.context.id_map.get(id_)

    def _get_group_children(self, id_):
        parent_node = self.context.id_map.get(id_)
        if not parent_node:
            logger.error('IDNotFound, id=' + id_)
            return []
        children = parent_node.get('children', [])
        for child in children:
            # update id_map
            if child['id'] not in self.context.id_map:
                self.context.id_map.update({
                    child['id']: child
                })

            self.add_parent_generator(child, parent_node)
            self.add_super_by(node=child)
        children.sort(key=lambda sub_node: sub_node['name'])
        return children

    def _get_link(self, _id):
        if not self.context.root:
            raise RootNotSet
        node = self.context.id_map.get(_id)
        if not node:
            raise IDNotFound(_id)

        link = node.get('link')
        if link:
            link_node = self.context.id_map.get(_id)
            if not link_node:
                logger.error('link node not found!')
                raise IDNotFound(link_node)
            data = self._get(node['link'])
            data['link'] = data['id']
            data['id'] = link_node['id']
            return data
        
    def _load_group(self, _id):
        data = self._get_link(_id)
        if data:
            return data
        return self.context.id_map.get(_id)

    def _add_group(self, data, **kwargs):
        ignore_key = self.add_group_ignore_keys | self.unsave_keys
        new_group = {k: data[k] for k in data if k not in ignore_key}

        parent_id = data.get('parent_id')
        if parent_id == None:
            parent_node = self.context.root
        else:
            parent_node = self.context.id_map.get(parent_id)

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
        self.context.id_map[group_id] = new_group
        # Save prop
        self._save_prop()
        return group_id

    def _update_group(self, data, **kwargs):
        id_ = data['id']
        node = self.context.id_map.get(id_)
        if not node:
            raise IDNotFound(id_)

        # 1. Add new key into node
        update_data = {k: data[k] for k in data if k not in self.update_group_ignore_keys}
        node.update(update_data)

        # 2. Remove deleted key in node
        delete_keys = [k for k in node if k not in data and k not in self.update_group_ignore_keys]
        for key in delete_keys:
            node.pop(key)

        # 3. Update existed value
        for key, value in data.items():
            if key in node:
                node[key] = value
        self._save_prop()

    def _delete(self, _id):
        target_node = self.context.id_map.get(_id)
        if not target_node:
            raise IDNotFound(_id)
        parent_id = target_node.get('parent_id')
        # Remove refs
        if parent_id:
            parent = self.context.id_map.get(parent_id)
            parent['children'].remove(target_node)
        else:
            self.context.root['children'].remove(target_node)
        self._delete_inner(_id)

    def _delete_inner(self, _id):
        target_node = self.context.id_map.get(_id)
        if not target_node:
            raise IDNotFound(_id)
        if 'children' in target_node and len(target_node['children']) > 0:
            for child in target_node['children'][::-1]:
                self._delete(child['id'])
        # Delete from ID mapping
        self.context.id_map.pop(_id)
        # Delete from mock tree
        self._delete_group(_id)
        # Delete from file system
        if target_node['type'] == 'data':
            self._delete_data(_id)

    def _delete_group(self, data):
        self._save_prop()

    def _delete_group_by_query(self, query):
        self._save_prop()
    
    def _batch_delete(self, query):
        node_delete_data_ids = query.get('data', [])
        node_delete_group_ids = query.get('groups', [])
        all_id_list = node_delete_data_ids + node_delete_group_ids
        
        for id_ in all_id_list:
            # Delete from parent
            self._delete_remove_from_parent(id_)

            # Delete from ID mapping
            self.context.id_map.pop(id_)
        
        self._delete_group_by_query({'id': node_delete_group_ids})
        self._delete_data_by_query({'id': node_delete_data_ids})

    def _get_type_hashmap(self, ids):
        type_map = {
            'group': [],
            'data': [],
            'json': [],
            'config': []
        }
        for id_ in ids:
            node = self.context.id_map.get(id_)
            if not node:
                continue
            node_type = node['type']
            if node_type not in type_map:
                continue
            type_map[node_type].append(id_)
        return type_map
    
    def _delete_remove_from_parent(self, id_):
        target_node = self.context.id_map.get(id_)
        if not target_node:
            return
        parent_id = target_node.get('parent_id')
        if not parent_id:
            return
        parent = self.context.id_map.get(parent_id)
        if not parent:
            return
        parent['children'].remove(target_node)

    """
    data
    """
    def _load_data(self, data_id, path=None):
        data = self._get_link(data_id)
        if data:
            return data

        if not path:
            path = self.root_path / data_id
        if not Path(path).exists():
            raise DataNotFound(f'Data file {path}')
        with codecs.open(path) as f:
            return json.load(f)

    def _load_data_by_query(self, query):
        datas = []
        for _id in query.get('id', []):
            datas.append(self._load_data(_id))
        return datas

    def _add_data(self, data, path=None, **kwargs):
        parent_id = kwargs.get('parent_id', None)
        data_type = kwargs.get('type', 'data')
        parent_node = self.context.id_map.get(parent_id)
        if not parent_node:
            raise IDNotFound(parent_id)
        
        if parent_node['type'] != 'group':
            raise OnlyGroupCanContainAnyOtherObject
        # Add data
        if not path:
            path = self.root_path / data['id']
        self._save_data(path, data)
        # Add group
        _data_id = data['id']
        if parent_node:
            data_node = {}
            data_node['id'] = _data_id
            data_node['name'] = data.get('name')
            data_node['type'] = data_type
            data_node['parent_id'] = parent_id
            if parent_node.get('children'):
                parent_node['children'].insert(0, data_node)
            else:
                parent_node['children'] = [data_node]

            # New data added in the head of child list
            logger.debug(f'*** Add to node {data_node}')
            # Update ID mapping
            self.context.id_map[_data_id] = data_node
            self._save_prop()

    def _delete_data(self, _id):
        data_file_path = self.root_path / _id
        os.remove(data_file_path)

    def _delete_data_by_query(self, query):
        for _id in query.get('id', []):
            self._delete_data(_id)

    def _update_data(self, _id, data):
        node = self.context.id_map.get(_id)
        if not node:
            raise IDNotFound(_id)
        if 'name' in data and node['name'] != data['name']:
            node['name'] = data['name']
        self._save_data(self.root_path/data['id'], data)
        self._update_group(node)

    def _paste(self, paste_info, **kwargs):
        group_id = paste_info.get('id')
        type = paste_info.get('type')
        parent_id = paste_info.get('parent_id')
        
        _parent_node = self.context.id_map.get(parent_id)
        _node = self.context.id_map.get(group_id)
        
        if not _parent_node:
            raise IDNotFound(parent_id)
        if not _parent_node.get('children'):
            _parent_node['children'] = []
        
        if type == 'cut':
            _origin_parent = self.context.id_map.get(_node['parent_id'])
            _origin_parent['children'].remove(_node)
            _parent_node['children'].insert(0, _node)
            _node['parent_id'] = parent_id
            _group_id = _node['id']
            self._update_group(_node)
        elif type == 'copy':
            new_name = _node['name'] + self.COPY_NODE_NAME_SUFFIX
            _group_id = self._copy_node(_parent_node, _node, paste_info, name=new_name, origin_name=_node['name'], **kwargs)
        elif type == 'import':
            _node = paste_info.get('node', {})
            _group_id = self._copy_node(_parent_node, _node, paste_info, **kwargs)
        return _group_id
    
    def _copy_node(self, parent_node, node, paste_info, **kwargs):
        if self.is_data_virtual_node(node):
            return
        # Generate new node
        new_node = {}
        new_node.update(node)
        new_node['id'] = str(uuid.uuid4())
        new_node['parent_id'] = parent_node['id']
        new_node['name'] = kwargs['name'] if kwargs.get('name') else new_node['name']
        new_node['children'] = []
        # Register ID
        self.context.id_map[new_node['id']] = new_node
        if new_node['type'] == 'group':
            parent_node['children'].insert(0, new_node)
            self._save_prop()
            kwargs.pop('name') if kwargs.get('name') else None
            kwargs.pop('origin_name') if kwargs.get('origin_name') else None
            for child in node['children']:
                self._copy_node(new_node, child, paste_info, **kwargs)
        elif new_node['type'] == 'data':
            self._copy_data(new_node, node, paste_info, **kwargs)
        elif new_node['type'] == 'json':
            self._copy_data(new_node, node, paste_info, **kwargs)
        return new_node['id']
    
    # TODO: 暂时不支持import
    def _copy_data(self, new_data_node, data_node, paste_info, **kwargs):
        _id = data_node['id']

        if paste_info.get('json'):
            event = paste_info.get('json', {}).get(_id)
            if not event:
                raise DataNotFound
            prop = {k:v for k,v in event.items()}
        elif paste_info.get('path'):
            with codecs.open(Path(paste_info['path'])/_id) as f:
                prop = json.load(f)
        else:
            prop = self._load_data(_id)

        prop['id'] = new_data_node['id']
        prop['name'] = kwargs.pop('name') if kwargs.get('name') else prop['name']
        self._add_data(prop, type=data_node['type'], parent_id=new_data_node['parent_id'])

    def is_data_virtual_node(self, node):
        if node['type'] == 'config':
            if 'link' in node:
                return node['link'] == self.virtual_base_config_id
 
        return False

    def _save_prop(self):
        # TODO: Handle frequent writes
        self._sort_children_by_name()
        prop_writer = PropWriter()
        prop_writer.dict_ignore_key.update(self.unsave_keys)

        # handle link node
        prop_writer.dict_ignore_child_key.add('link')

        prop_str = prop_writer.parse(self.context.root)
        prop_file = self.root_path / PROP_FILE_NAME
        with codecs.open(prop_file, 'w') as f:
            f.write(prop_str)

    def _save_data(self, path, data):
        new_data = deepcopy(data)
        new_data.pop('type', None)
        prop_str = json.dumps(new_data, ensure_ascii=False)
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
    
    def _activate(self, search_id):
        if not self.context.root:
            raise RootNotSet
        _node = self.context.id_map.get(search_id)
        if not _node:
            raise IDNotFound(f'ID:{search_id}')
        node_id_list = self._collect_activate_node(_node, level_lefted=self.LEVEL_SUPER_ACTIVATED)
        ordered_data_id = []
        for node_id in node_id_list:
            activated_node = self.context.id_map.get(node_id)
            ordered_data_id += self._collect_data_in_node(activated_node)
        node_list = self._load_data_by_query({'id': ordered_data_id})
        config = {}
        for node in node_list:
            node_in_map = self.context.id_map.get(node.get('id'))
            if node_in_map['type'] == 'config':
                config = node
        return {
            'config': config,
            'flows': node_list,
            'groupInfo': _node
        }

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

    def _collect_activate_node(self, node, level_lefted=1):
        id_list = [node['id']]
        if level_lefted <= 0:
            return id_list
        if not node.get('super_id'):
            return id_list
        if node.get('super_id') == node['id']:
            raise SuperIdCannotBeNodeItself(node['id'])

        _super_id = node.get('super_id')
        _super_node = self.context.id_map.get(_super_id)
        if not _super_node:
            raise IDNotFound(f'Super node ID: {_super_id}')

        id_list.extend(self._collect_activate_node(_super_node, level_lefted=level_lefted-1))
        return id_list

    def _get_activate_group(self, search_id):
        return self.context.id_map.get(search_id)

    def _after_activate(self, **kwargs):
        pass

    def add_parent(self, node=None):
        if not node:
            root_id = self.context.root['id']
            root = self.context.id_map.get(root_id)
            self.add_parent_generator(root)
        else:
            parent_node = self.context.id_map.get(node['parent_id'])
            self.add_parent_generator(node, parent_node=parent_node)
        self.unsave_keys.update(['parent', 'abs_parent_path'])
    
    def add_super_by(self, node=None):
        node_list = [node] if node else self.context.id_map.values()

        for node in node_list:
            if not node.get('super_id'):
                continue
            super_parent_node = self.context.id_map.get(node['super_id'])
            if not super_parent_node:
                continue
            if not super_parent_node.get('super_by'):
                super_parent_node['super_by'] = []
            super_parent_node['super_by'].append({
                'id': node['id'],
                'name': node['name']
            })
        self.unsave_keys.add('super_by')

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

    def _sort_children_by_name(self):
        for node_id in self.context.id_map:
            node = self.context.id_map[node_id]
            if 'children' not in node:
                # fix mock data group has no children
                if node['type'] == 'group':
                    node['children'] = []
                continue
            node['children'] = sorted(node['children'], key=lambda sub_node: sub_node['name'])

    def _search(self, search_str, sender=None):
        _matched_group = []
        if search_str:
            if self.context.id_map.get(search_str):
                # search_str is group id
                group = self.context.id_map.get(search_str)
                _matched_group.append(self.make_search_group_item(group))
            else:
                for _id, group in self.context.id_map.items():
                    if group.get('type') == 'group' and search_str.lower() in group.get('name', '').lower():
                        _matched_group.append(self.make_search_group_item(group))
        else:
            for _id, group in self.context.id_map.items():
                if group.get('type') == 'group' and group.get('name'):
                    _matched_group.append(self.make_search_group_item(group))
        logger.info(f'搜索到{len(_matched_group)}个数据组')
        return _matched_group

    def make_search_group_item(self, _group):
        return {
                'id': _group['id'],
                'name': _group['name'],
                'type': _group['type'],
                'parent_id': _group['parent_id'],
                'abs_parent_path': self._get_abs_parent_path(_group),
                'abs_parent_obj': self._get_abs_parent_obj(_group)
            }
    
    def _get_abs_parent_path(self, data, path='/'):
        id = data.get('id')
        if not id:
            return path
       
        node = self.context.id_map.get(id)
        if 'parent_id' in node:
            parent_node = self.context.id_map.get(node['parent_id'])
        
        if not parent_node:
            return path
        current_path = '/' + node['name'] + path
        return self._get_abs_parent_path(parent_node, path=current_path)
    
    def _get_node_parent(self, node):
        if 'parent_id' not in node:
            return None
        parent_node = self.context.id_map.get(node['parent_id'])
        if not parent_node:
            return None
        return parent_node
    
    def _get_abs_parent_obj(self, node, parent_obj=None):
        if parent_obj is None:
            parent_obj = []
        if 'id' not in node:
            return parent_obj
        node_info = self.context.id_map.get(node['id'])
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
    
    def _get_node_prop(self, _id):
        node = self.context.id_map.get(_id)
        ordered_data_id = self._collect_data_in_node(node)
        return {
            'prop': node,
            'childDataIds': ordered_data_id
        }

    # -----
    # Get all data under one id
    # -----

    def _read_data(self, _id):
        node = self.context.id_map.get(_id)
        if not node:
            raise IDNotFound(_id)
        data_array = []
        if node.get('type') == 'data':
            _data = self._load_data(node['id'])
            _data['parent_id'] = node['parent_id']
            data_array.append(_data)
        elif node.get('type') == 'group':
            for child in node['children']:
                data_array.extend(self._read_data(child.get('id')))
        return data_array

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
        self.dict_ignore_child_key = set()

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
            if self.dict_ignore_child_key & set(child.keys()):
                continue
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


class RootNotSet(Exception):
    pass

class UnsupportedType(Exception):
    pass


class OnlyGroupCanContainAnyOtherObject(Exception):
    pass


class SuperIdCannotBeNodeItself(Exception):
    pass


data_adapter = FileDataAdapter
