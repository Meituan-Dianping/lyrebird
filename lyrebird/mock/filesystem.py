import codecs
import copy
import json
import os
import shutil
from functools import reduce
from urllib import parse as url_parser
from typing import Dict
from pathlib import Path
import traceback
from flask import Response
from lyrebird import log
from . import context
import sys


_logger = log.get_logger()

"""
文件管理系统

用于管理存储在文件中mock数据，数据组

"""

class FileSystemError(Exception):
    pass


class FileManager:
    """
    FileSystem入口
    
    管理整个mock服务器的数据文件
    
    数据文件以数据组的形式保存于数据目录下，每个数据组下包含若干组数据和一个匹配规则文件。
    数据组之间可以继承[注意:不要循环继承]。
    """
    def __init__(self):
        self.data_dir = None
        self.data_groups: Dict[str, DataGroup] = dict()
        self.current_data_group = None

    def set_temp_group(self, path):
        temp_group = DataGroup.create_from_dir(path)
        self.current_data_group = temp_group

    def set_root(self, path):
        data_root = Path(path).absolute()
        if not data_root.exists():
            try:
                data_root.mkdir(parents=True)
            except Exception:
                _logger.error(f'Data root path not found. And make new dir failed. {path}')
                raise FileSystemError(f'Data root path not found. And make new dir failed. {path}')
        if not os.path.isdir(path):
            raise FileSystemError(f'Set data root path fail. {path} is not a dir')
        self.data_dir = path
        self.scan()

    def scan(self):
        self.data_groups.clear()
        # 由于数据组只存在于数据目录下，因此没有递归查找的处理
        data_group_dir_names = os.listdir(self.data_dir)
        for dir_name in data_group_dir_names:
            group = DataGroup.create_from_dir(os.path.join(self.data_dir, dir_name))
            if group:
                self.data_groups[group.name] = group

    def add_group(self, name, json_obj):
        """
        新建数据组

        如果数据组已存在，则新数据与旧数据组合并

        """
        group_abspath = os.path.abspath(os.path.join(self.data_dir, name))
        if not os.path.exists(group_abspath):
            os.mkdir(group_abspath)
        new_group = DataGroup.create_from_data(group_abspath, json_obj)
        old_group = self.data_groups.get(name)
        if old_group:
            old_group.merge(new_group)
        else:
            self.data_groups[new_group.name] = new_group
        self.scan()

    def update_group(self, origin_name, name, json_obj):
        """
        更新数据组

        """
        group = self.data_groups.get(origin_name)
        if group:
            group.conf = json_obj
            group.write_conf()
            if origin_name != name:
                group.rename(name)
        self.scan()

    def set_current_data_group(self, name):
        if not name or name == '':
            self.current_data_group = None
            return True
        target_group = self.data_groups.get(name)
        if target_group:
            self.current_data_group = target_group
            return True
        else:
            return False


class DataGroup:
    """
    Mock数据组
    
    根据数据组目录下conf.json文件,判断请求是否匹配某一条mock数据。
    如果匹配则返回mock数据中的response。
    如果不匹配则返回None。
    
    """
    CONF = 'conf.json'

    @classmethod
    def create_from_data(cls, dir_path, json_data):
        group = cls(dir_path)
        group.conf = json_data
        group.write_conf()
        group.scan()
        return group

    @classmethod
    def create_from_dir(cls, dir_path):
        if not os.path.isdir(dir_path):
            return None
        sub_file_names = os.listdir(dir_path)
        if DataGroup.CONF not in sub_file_names:
            return None
        group = cls(dir_path)
        group.read_conf()
        group.scan()
        return group

    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.name = os.path.basename(dir_path)
        self.conf_path = os.path.abspath(os.path.join(dir_path, DataGroup.CONF))
        self.conf = None
        self.data_dict: Dict[str, Data] = {}

    def scan(self):
        self.data_dict = {}
        sub_file_names = os.listdir(self.dir_path)
        for file_name in sub_file_names:
            data = Data.create_from_dir(os.path.join(self.dir_path, file_name))
            if data:
                self.data_dict[data.name] = data

    def merge(self, group):
        self.conf['filters'] += group.conf['filters']
        self.conf['parent'] = group.conf['parent']
        self.write_conf()

    def rename(self, name):
        new_path = os.path.join(os.path.dirname(self.dir_path), name)
        os.rename(self.dir_path, new_path)
        self.name = name
        self.dir_path = os.path.abspath(new_path)
        self.conf_path = os.path.abspath(os.path.join(new_path, DataGroup.CONF))

    def delete(self):
        shutil.rmtree(self.dir_path)

    def read_conf(self):
        try:
            self.conf = json.loads(codecs.open(self.conf_path, 'r', 'utf-8').read())
        except Exception as e:
            exc_info = sys.exc_info()
            _logger.error(f'Read conf error. \nFile:{self.conf_path}. \nClass:{exc_info[0]} \nMessage:{exc_info[1]}')
            raise FileSystemError(f'Read conf error. File={self.conf_path}') from e

    def write_conf(self):
        f = codecs.open(self.conf_path, 'w', 'utf-8')
        conf_str = json.dumps(self.conf, ensure_ascii=False, indent=4)
        f.write(conf_str)
        f.close()

    def get_response(self, url, requset_data = None):
        for req_filter in self.conf['filters']:
            contents = req_filter['contents']
            # 跳过空的过滤条件
            if len(contents) == 0:
                continue
            # 检查filters/contents中的字符是否都在url中
            hit = True
            for content in contents:
                if content not in url:
                    hit = False
                    break
            # 判断filters／request是否存在（手工配置），且当前url的requset_data不为空，则进行对比校验
            if hit and 'body_filter' in req_filter.keys() and requset_data != None:
                try:
                    if req_filter['body_filter'] not in requset_data.decode():
                        hit = False
                except Exception:
                    traceback.print_exc()
                    _logger.error(f'请检查config文件，URL为{contents}是否配置了body_filter字段，会触发对请求参数的校验!')
            # 如果未命中继续查找
            if not hit:
                continue
            # 命中, 返回mock数据
            data = self.data_dict[req_filter['response']]
            resp_headers = [('lyrebird', 'mock;'+data.name)]
            for item in data.resp_headers:
                if isinstance(item, str):
                    name = item
                    value = data.resp_headers[name]
                elif isinstance(item, list):
                    name = item[0]
                    value = item[1]
                else:
                    continue
                # rm 'content-length' from ignore list
                if name.lower() in ('connection',
                                    'content-encoding',
                                    'transfer-encoding'):
                    continue
                resp_headers.append((name, value))
            return Response(data.resp_data, data.resp_code, resp_headers)
        # 如果conf中配置了parent，开始递归查找
        if self.conf.get('parent'):
            parent_path = self.conf['parent']
            if not os.path.isabs(parent_path):
                parent_path = os.path.abspath(os.path.join(self.dir_path, parent_path))
            if not os.path.exists(parent_path):
                raise FileSystemError('Can not find parent data group')
            parent_group = DataGroup.create_from_dir(parent_path)
            return parent_group.get_response(url)
        # 没有匹配任何数据
        return None

    def add_data(self, name, json_data):
        data_dir = os.path.join(self.dir_path, name)
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)
        Data.create_from_data(data_dir, json_data)
        self.scan()

    def update_data(self, origin_name, name, json_data):
        data = self.data_dict.get(origin_name)
        data.json_data = json_data
        data.write_file()
        data.rename(name)
        self.scan()
    
    def add_data_and_filter(self, flow):
        url = flow['request']['url']
        result = url_parser.urlparse(url)
        resp_name = result.path.replace('/', '.')[1:]+'_'+flow['id']
        self.add_data(resp_name, flow)
        # TODO make simple filters.
        if result.path == '' or result.path == '/':
            filter_contents = [result.hostname]
        else:
            filter_contents = [result.path]
        self.conf['filters'].append({'contents':filter_contents, 'response':resp_name})
        self.write_conf()
        self.scan()

class Data:
    """
    Mock数据文件管理
    
    request.json
    >保存请求头，URL
    
    request_data.json
    request_data.form
    request_data.bin
    >保存请求体，根据不同格式扩展名不同
    
    response.json
    >响应状态码，响应头
    
    response_data.json
    response_data.bin
    >响应数据，根据不同格式扩展名不同
    
    """
    @classmethod
    def create_from_data(cls, data_dir, json_data):
        data = cls(data_dir)
        data.json_data = json_data
        data.write_file()
        return data

    @classmethod
    def create_from_dir(cls, data_dir):
        if not os.path.isdir(data_dir):
            return None
        return cls(data_dir)

    def __init__(self, path):
        self.name = os.path.basename(path)
        self.path = path
        self.json_data = None

    @property
    def resp_data(self):
        contents = os.listdir(self.path)
        if 'response_data.json' in contents:
            resp_body_file = os.path.join(self.path, 'response_data.json')
        elif 'response_data.bin' in contents:
            resp_body_file = os.path.join(self.path, 'response_data.bin')
        else:
            return ''
        f = codecs.open(resp_body_file, 'r', 'utf-8')
        res = f.read()
        f.close()
        return res

    @property
    def resp_headers(self):
        f = codecs.open(os.path.join(self.path, 'response.json'))
        resp = json.loads(f.read())
        f.close()
        return resp['headers']

    @property
    def resp_code(self):
        f = codecs.open(os.path.join(self.path, 'response.json'))
        resp = json.loads(f.read())
        f.close()
        return resp['code']

    def rename(self, name):
        new_path = os.path.join(os.path.dirname(self.path), name)
        os.rename(self.path, new_path)
        self.name = name
        self.path = new_path

    def write_file(self):
        if not self.json_data:
            raise FileSystemError('Write to file error. Not set json data')
        req = self.json_data.get('request')
        if req:
            req_header = {'url': req.get('url'), 'method': req.get('method', 'GET'), 'headers': req.get('headers')}
            if req_header:
                self._write_file('request', req_header)
            req_data = req.get('data')
            if req_data:
                self._write_file('request_data', req_data)
        resp = self.json_data.get('response')
        if resp:
            # 保存时去掉数据源标记
            resp_header = {'code': resp.get('code', 200), 'headers': copy.deepcopy(resp.get('headers'))}
            resp_header['headers'].pop('lyrebird', None)
            if resp_header:
                self._write_file('response', resp_header)
            resp_data = resp.get('data')
            if resp_data:
                self._write_file('response_data', resp_data)

    def _write_file(self, name, data):
        if isinstance(data, (str, bytes)):
            name = name + '.bin'
            if isinstance(data, str):
                data = data.encode()
            f = codecs.open(os.path.join(self.path, name), 'wb')
            f.write(data)
            f.close()
        elif isinstance(data, (dict, list)):
            name = name + '.json'
            data = json.dumps(data, ensure_ascii=False, indent=4)
            f = codecs.open(os.path.join(self.path, name), 'w', 'utf-8')
            f.write(data)
            f.close()
        else:
            raise FileSystemError(f'Write to file error. Unsupported type {type(data)}')

    def read_file(self):
        self.json_data = dict()
        req_h = self._read_file('request')
        req_data = self._read_file('request_data')
        self.json_data['request'] = req = dict()
        if req_h:
            req['url'] = req_h.get('url')
            req['method'] = req_h.get('method')
            req['headers'] = req_h.get('headers')
        if req_data:
            req['data'] = req_data
        resp_h = self._read_file('response')
        resp_data = self._read_file('response_data')
        self.json_data['response'] = resp = dict()
        if resp_h:
            resp['code'] = resp_h.get('code')
            resp['headers'] = resp_h.get('headers')
        if resp_data:
            resp['data'] = resp_data

    def _read_file(self, name):
        file_path = os.path.join(self.path, name+'.json')
        if os.path.exists(file_path):
            return json.loads(codecs.open(file_path, 'r', 'utf-8').read())
        file_path = os.path.join(self.path, name+'.bin')
        if os.path.exists(file_path):
            return codecs.open(file_path, 'rb').read().decode()

    def delete(self):
        shutil.rmtree(self.path)


class DataGroupConfBuilder:

    def __init__(self):
        self.host = False
        self.path = True
        self.split_path = False
        self.query = False
        self.split_query = False
        self._conf = dict()
        self._conf['parent'] = None
        self._conf['filters'] = []

    def add_filter_by_req_ctx(self, req_ctx_dict):
        conf = context.application.conf
        _filter = dict()
        url_filter_contents = []
        ctx_id = req_ctx_dict['id']
        url = req_ctx_dict['request']['url']
        result = url_parser.urlparse(url)
        ''' hotfix new conf did not contains record settings
        if conf.get('mock') and conf.get('mock').get('record'):
            record = conf.get('mock').get('record')
            self.host = record.get('host', self.host)
            self.path = record.get('path', self.path)
            self.split_path = record.get('split_path', self.split_path)
            self.query = record.get('query', self.query)
            self.split_query = record.get('split_query', self.split_query)
        '''
        if self.host:
            url_filter_contents.append(result.hostname)
        if self.path and len(result.path) > 1:
            if self.split_path:
                path_items = result.path.split('/')
                url_filter_contents += path_items
            else:
                url_filter_contents.append(result.path)
        if self.query and len(result.query) > 0:
            if self.split_query:
                query_items = result.query.split('&')
                url_filter_contents += query_items
            else:
                url_filter_contents.append(result.query)
        _filter['contents'] = list(filter(lambda x: True if len(x) > 0 else False, url_filter_contents))
        _filter['response'] = result.path.replace('/', '.')[1:] + '_' + ctx_id
        self._conf['filters'].append(_filter)
        return self

    def build(self):
        return self._conf


class DataHelper:

    @staticmethod
    def to_dict(req, req_data, resp, resp_data):
        data = dict()
        req_dict = data['request'] = dict()
        if req:
            req_dict.update(json.loads(req))
        if req_data:
            try:
                req_data = json.loads(req_data)
            except Exception:
                pass
            req_dict['data'] = req_data
        resp_dict = data['response'] = dict()
        if resp:
            resp_dict.update(json.loads(resp))
        if resp_data:
            try:
                resp_data = json.loads(resp_data)
            except Exception:
                pass
            resp_dict['data'] = resp_data
        return data
