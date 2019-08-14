import json
import codecs
from pathlib import Path
import argparse
import uuid
import shutil
from urllib.parse import urlparse
import traceback
from lyrebird.log import get_logger


logger = get_logger()


NEW_INFO_FILENAME = '.lyrebird_prop'
OLD_INFO_FILENAME = 'conf.json'


class WorkDirNotExists(Exception):
    pass


class WorkDirIsNotDir(Exception):
    pass


def update(work_dir, output_dir):
    if not work_dir.exists():
        raise WorkDirNotExists(f'{work_dir} not exists')
    if not work_dir.is_dir():
        raise WorkDirIsNotDir(f'{work_dir} is not dir')

    output_dir.mkdir(parents=True, exist_ok=True)

    work_dir = work_dir.expanduser().absolute()
    output_dir = output_dir.expanduser().absolute()
    print(f'work dir is {work_dir} Output dir is {output_dir}')
    
    for group_dir_name in Path(work_dir).iterdir():
        try:
            update_group(work_dir/group_dir_name.name, output_dir/group_dir_name.name)
        except Exception as e:
            logger.error(f'!!! Load group fail. {e}. {group_dir_name} . [removed]')
            traceback.print_exc()
            shutil.rmtree(str(output_dir/group_dir_name.name))


def update_group(group_dir, output_group_dir):
    old_conf_file = group_dir/OLD_INFO_FILENAME
    if not old_conf_file.exists():
        logger.error(f'Dir {group_dir} is not data group. skip >>')
        return

    print(f'Working in group {group_dir}')
    with codecs.open(old_conf_file, 'r', 'utf-8') as f:
        old_conf = json.load(f)

    output_group_dir.mkdir(exist_ok=True)
    print(f'Copy to target {output_group_dir}')

    new_group_info = {
        "id": str(uuid.uuid4()),
        "name": group_dir.name,
        "parent": None
    }
    with codecs.open(output_group_dir/NEW_INFO_FILENAME, 'w', 'utf-8') as f:
        json.dump(new_group_info, f, ensure_ascii=False, indent=4)

    saved_filter = set()
    for data_filter in old_conf['filters']:
        data_name = data_filter.get('response')
        if not data_name:
            logger.error(f'Bad data: not set response data. {data_filter}')
            continue
        contents = data_filter.get('contents')
        if not contents:
            logger.error(f'Bad data: not set filter. {data_filter}')
            continue
        filter_key = '.*'.join(contents)
        if filter_key in saved_filter:
            logger.error(f'Bad data: duplicate filter. {data_filter} -[removed]')
            continue
        try:
            update_data(group_dir/data_name, output_group_dir/data_name, old_group_filter=contents)
            saved_filter.add(filter_key)
        except Exception as e:
            logger.error(f'!!! Load data error. {e} . {group_dir/data_name}')
            traceback.print_exc()


def update_data(data_dir, output_data_dir, old_group_filter=None):
    print(f'Working in data {data_dir}')

    output_data_dir.mkdir(exist_ok=True)

    req = data_dir/'request.json'
    req_data = data_dir/'request_data.json'
    req_data_bin = data_dir/'request_data.bin'

    resp = data_dir/'response.json'
    resp_data = data_dir/'response_data.json'
    resp_data_bin = data_dir/'response_data.bin'

    req_obj = {}
    with codecs.open(req, 'r', 'utf-8') as f:
        req_obj = json.load(f)
    with codecs.open(output_data_dir/'request', 'w', 'utf-8') as f:
        json.dump({
            'url': req_obj.get('url'),
            'method': req_obj.get('method'),
            'headers': req_obj.get('headers')
        }, f, ensure_ascii=False, indent=4)
    
    if req_data.exists():
        shutil.copy(req_data, output_data_dir/'request_data')
    elif req_data_bin.exists():
        shutil.copy(req_data_bin, output_data_dir/'request_data')
    
    resp_obj = {}
    with codecs.open(resp, 'r', 'utf-8') as f:
        resp_obj = json.load(f)
    with codecs.open(output_data_dir/'response', 'w', 'utf-8') as f:
        json.dump({
            "code": resp_obj.get('code'),
            "headers": resp_obj.get('headers')
        }, f, ensure_ascii=False, indent=4)
    
    if resp_data.exists():
        shutil.copy(resp_data, output_data_dir/'response_data')
    elif resp_data_bin.exists():
        shutil.copy(resp_data_bin, output_data_dir/'response_data')

    new_data_info = {
                'id': str(uuid.uuid4()),
                'name': "",
                'rule': {},
                'request_data_type': None,
                'response_data_type': None
            }

    url = req_obj.get('url')
    if url:
        parsed_url = urlparse(url)
        if parsed_url.path != '/' and parsed_url.path != '':
            new_data_info['name'] = parsed_url.path
        else:
            new_data_info['name'] = parsed_url.hostname

    regex = ''
    for filter_line in old_group_filter:
        regex += f'(?=.*{filter_line})'
    new_data_info['rule'] = {'request.url': regex}

    content_type = req_obj.get('headers', {}).get('Content-Type')
    if content_type:
        if 'json' in content_type:
            new_data_info['request_data_type'] = 'json'
        elif 'html' in content_type:
            new_data_info['request_data_type'] = 'html'
        elif 'xml' in content_type:
            new_data_info['request_data_type'] = 'xml'
        elif 'text' in content_type:
            new_data_info['request_data_type'] = 'text'
    
    content_type = resp_obj.get('headers', {}).get('Content-Type')
    if content_type:
        if 'json' in content_type:
            new_data_info['response_data_type'] = 'json'
        elif 'html' in content_type:
            new_data_info['response_data_type'] = 'html'
        elif 'xml' in content_type:
            new_data_info['response_data_type'] = 'xml'
        elif 'text' in content_type:
            new_data_info['response_data_type'] = 'text'
    
    with codecs.open(output_data_dir/NEW_INFO_FILENAME, 'w', 'utf-8') as f:
        json.dump(new_data_info, f, ensure_ascii=False, indent=4)


def check_data_dir(data_root_path):
    data_dir = Path(data_root_path)
    data_dir.mkdir(exist_ok=True)
    if (data_dir/NEW_INFO_FILENAME).exists():
        return
    # Move data dir for data format
    old_dir = data_dir.parent/(data_dir.name+'_old')
    if old_dir.exists():
        shutil.rmtree(old_dir)
    shutil.move(data_dir, old_dir)
    # Transform old data
    update(old_dir, data_dir)
    # Touch new data prop file
    (data_dir/NEW_INFO_FILENAME).touch()

def main():
    parser = argparse.ArgumentParser(prog='DataFormatUpdateHelper')
    parser.add_argument('-d', '--dir', dest='root_dir', help='Set target data root dir')
    parser.add_argument('-o', '--output', dest='output_dir', help='Set output root dir')

    args = parser.parse_args()
    if not args.root_dir:
        work_dir = Path('.')
    else:
        work_dir = Path(args.root_dir)
    if not args.output_dir:
        output_dir = Path('./output')
    else:
        output_dir = Path(args.output_dir)
    update(work_dir, output_dir)


if __name__ == '__main__':
    main()
