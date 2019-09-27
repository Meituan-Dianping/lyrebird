import codecs
import json
from pathlib import Path
import os
from lyrebird.log import get_logger
import uuid
from lyrebird.mock.dm import PropWriter

logger = get_logger()

id_map = {}
root = {
    'id': str(uuid.uuid4()),
    'name': '$',
    'type': 'group',
    'parent_id': None,
    'children': []
}
data_root_dir = None


def check_data_version(data_dir):
    prop_file_name = '.lyrebird_prop'
    data_root_path = Path(data_dir).expanduser()
    if not data_root_path.is_dir():
        raise NotDir(f'{data_dir}')
    # empty dir - mock data v2
    file_list = os.listdir(data_root_path)
    if len(file_list) == 0:
        return '1.7.0'
    prop_file = data_root_path / prop_file_name
    # alpha version
    if not prop_file.exists():
        return '0.15.0'
    with codecs.open(prop_file) as f:
        prop_content = f.read()
    # mock data v1
    if len(prop_content) == 0:
        return '1.0.0'
    json.loads(prop_content)
    # mock data v2
    return '1.7.0'


def update(data_dir):
    global root
    global data_root_dir
    data_root_dir = Path(data_dir)
    _backup_dir = _backup(data_dir)
    for data_groups_dir in Path(_backup_dir).iterdir():
        if not data_groups_dir.is_dir():
            continue
        _load_mock_group(data_groups_dir)
    prop_str = PropWriter().parse(root)
    with codecs.open(Path(data_dir) / '.lyrebird_prop', 'w', 'utf-8') as f:
        f.write(prop_str)


def _load_mock_group(group_dir):
    global id_map
    global root
    logger.log(60, f'Load mock data group from {group_dir}')
    group_prop_file = group_dir / '.lyrebird_prop'
    group_prop = {
        'id': None,
        'name': None,
        'parent_id': root['id'],
        'type': 'group',
        'super_id': None,
        'children': []
    }
    with codecs.open(group_prop_file, 'r', 'utf-8') as f:
        _group_prop = json.load(f)
        if 'parent' in _group_prop:
            group_prop['super_id'] = _group_prop['parent']
            del _group_prop['parent']
        group_prop.update(_group_prop)
    for data_dir in group_dir.iterdir():
        if not data_dir.is_dir():
            continue
        data_prop = _load_mock_data(data_dir, group_prop['id'])
        if data_prop:
            group_prop['children'].append(data_prop)
    root['children'].append(group_prop)
    id_map[group_prop['id']] = group_prop


def _load_mock_data(data_dir, parent_id):
    global id_map
    global data_root_dir
    logger.log(60, f'Load data from {data_dir}')
    data_prop_file = data_dir / '.lyrebird_prop'
    if not data_prop_file.exists():
        logger.error(f'Not found prop file in {data_dir}')
        return
    data_prop = {
        'id': None,
        'name': None,
        'parent_id': parent_id,
        'type': 'data'
    }
    with codecs.open(data_prop_file, 'r', 'utf-8') as f:
        _data_prop = json.load(f)
        data_prop['id'] = _data_prop['id']
        data_prop['name'] = _data_prop['name']
        id_map[data_prop['id']] = data_prop
    _save_data_to_file(data_dir, data_root_dir/data_prop['id'])
    return data_prop


def _save_data_to_file(data_dir, dist, _id=None):
    data_root = Path(data_dir)
    _prop = data_root / '.lyrebird_prop'
    _req = data_root / 'request'
    _req_data = data_root / 'request_data'
    _resp = data_root / 'response'
    _resp_data = data_root / 'response_data'
    prop = json.load(codecs.open(_prop))
    if _id:
        prop['id'] = _id
    if _req.exists():
        prop['request'] = json.load(codecs.open(_req))
        if _req_data.exists():
            with codecs.open(_req_data) as f:
                prop['request']['data'] = f.read()
    if _resp.exists():
        prop['response'] = json.load(codecs.open(_resp))
        if _resp_data.exists():
            with codecs.open(_resp_data) as f:
                prop['response']['data'] = f.read()
    with codecs.open(dist, 'w') as f:
        json.dump(prop, f, ensure_ascii=False)


def _backup(data_dir):
    _backup_dir = str(data_dir)+'_bak'
    os.rename(str(data_dir), str(data_dir)+'_bak')
    os.mkdir(data_dir)
    logger.warning(f'\n----------------\nMock data backup was saved to {_backup_dir}\n----------------\n')
    return _backup_dir


class IDNotFound(Exception):
    pass


class NotDir(Exception):
    pass


class PropFileNotFound(Exception):
    pass
