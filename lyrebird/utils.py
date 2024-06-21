import re
import os
import json
import math
import time
import uuid
import redis
import pickle
import socket
import tarfile
import requests
import datetime
import netifaces
import traceback
from pathlib import Path
from copy import deepcopy
from jinja2 import Template, StrictUndefined
from jinja2.exceptions import UndefinedError, TemplateSyntaxError
from contextlib import closing
from urllib.parse import unquote
from lyrebird.log import get_logger
from lyrebird.application import config

logger = get_logger()

REDIS_EXPIRE_TIME = 60*60*24

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def convert_size_to_byte(size_str: str):
    size_str = size_str.strip().upper()
    match = re.match(r'^(\d+\.?\d*)\s*([KMGTPEZY]?[B])$', size_str)
    if not match:
        logger.warning(f'Invalid size string: {size_str}')
        return
    size = float(match.group(1))
    unit = match.group(2)
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = size_name.index(unit)
    size_bytes = int(size * (1024 ** i))
    return size_bytes


def convert_time(duration):
    if duration < 1:
        return str(round(duration * 1000)) + 'ms'
    else:
        return str(round(duration, 2)) + 's'


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print(f'{method.__name__} execution time {(te-ts)*1000}')
        return result
    return timed


def is_port_in_use(port, host='127.0.0.1'):
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((host, int(port)))
        return True
    except socket.error:
        return False
    finally:
        if sock:
            sock.close()


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def get_ip():
    """
    Get local ip from socket connection

    :return: IP Addr string
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


def get_interface_ipv4():
    ipv4_list = []
    interface_list = netifaces.interfaces()
    for interface_name in interface_list:
        if interface_name == 'lo0':
            continue
        interface_dict = netifaces.ifaddresses(interface_name)
        interface = interface_dict.get(netifaces.AF_INET)
        if not interface:
            continue
        for alias in interface:
            ipv4_list.append({
                'address': alias['addr'],
                # windows keyerror 'netmask'
                # https://github.com/Meituan-Dianping/lyrebird/issues/665
                'netmask': alias.get('netmask', ''),
                'interface': interface_name
            })
    return ipv4_list


def compress_tar(input_path, output_path, suffix=None):
    current_path = Path.cwd()
    input_path = Path(input_path).expanduser().absolute().resolve()
    output_path = Path(output_path).expanduser().absolute().resolve()
    output_file = f'{output_path}{suffix}' if suffix else output_path

    os.chdir(input_path)
    # If not chdir, the directory in the compressed file will start from the root directory
    tar = tarfile.open(output_file, 'w:gz')
    for root, dirs, files in os.walk(input_path):
        for f in files:
            tar.add(f, recursive=False)
    tar.close()
    os.chdir(current_path)
    return output_file


def decompress_tar(input_path, output_path=None):
    input_path = Path(input_path).expanduser().absolute().resolve()
    if not output_path:
        filename = input_path.stem if input_path.suffix else f'{input_path.name}-decompress'
        output_path = input_path.parent / filename

    tf = tarfile.open(str(input_path))
    tf.extractall(str(output_path))
    tf.close()
    return output_path


def download(link, input_path):
    resp = requests.get(link, stream=True)
    with open(input_path, 'wb') as f:
        for chunck in resp.iter_content():
            f.write(chunck)


def handle_jinja2_tojson_by_config(data):
    config_value_tojson_key = config.get('config.value.tojsonKey')
    data_with_tojson = data
    for tojson_key in config_value_tojson_key:

        # EXAMPLE
        # response_data = `"key1":"value1","key2":"{{config.get('model.id')}}","key3":"value3"`
        # target_match_data = `"{{config.get('model.id')}}"`
        # Divide target_match_data into three parts `"{{` and `config.get('model.id')` and `}}"`
        # In the second part, `model.id` is a matching rule from Lyrebird configuration
        # The final return response_data is `"key1":"value1","key2":{{config.get('model.id') | tojson}},"key3":"value3"`

        pattern = '[^:]*' + tojson_key + '[^,]*'
        # The format of the group is required
        pattern_group = '(' + pattern + ')'
        data_with_tojson = re.sub('("{{)'+pattern_group+'(}}")', r'{{\2 | tojson}}', data_with_tojson)
    return data_with_tojson


def handle_jinja2_keywords(data, params=None):
    '''
    Jinja2 will throw an exception when dealing with unexpected left brackets, but right brackets will not
    So only left brackets need to be handled

    Handle 3 kinds of unexpected left brackets:
    1. More than 2 big brackets              `{{{ }}}` `{{# #}}` `{{% %}}`
    2. Mismatched keyword                    `{{{` `{{#` `{{%`
    3. Unknown arguments between {{ and }}   `{{unknown}}`

    Convert unexpected brackets into presentable string in Jinja2, such as `var` -> `{{ 'var' }}`
    The unexpected left brackets above will be convert into:
    `{{#`          ->  `{{ '{{#' }}`
    `{{unknown}}`  ->  `{{ '{{' }}unknown{{ '}}' }}`
    '''

    keywords_pair = {
        '{{': '}}',
        '{%': '%}',
        '{#': '#}'
    }

    # split by multiple `{` followed by `{` or `#`` or `%`, such as `{{`, `{{{`, `{{{{`, `{#`, `{{#`
    # EXAMPLE
    # data = '{{ip}} {{ip {{{ip'
    # item_list = ['', '{{', 'ip}} ', '{{', 'ip ', '{{{', 'ip']
    item_list = re.split('({+[{|#|%])', data)
    if len(item_list) == 1:
        return data

    left_pattern_index = None
    for index, item in enumerate(item_list):
        if index % 2:
            # 1. Handle more than 2 big brackets
            if (len(item) > 2) or (item not in keywords_pair):
                item_list[index] = "{{ '%s' }}" % (item)
            else:
                left_pattern_index = index
            continue

        if left_pattern_index is None:
            continue

        left_pattern = item_list[left_pattern_index]
        left_pattern_index = None

        # 2. Handle mismatched keyword
        right_pattern = keywords_pair[left_pattern]
        if right_pattern not in item:
            item_list[index-1] = "{{ '%s' }}" % (item_list[index-1])
            continue

        # 3. Handle unknown arguments between {{ and }}
        if left_pattern == '{{':
            key_n_lefted = item.split('}}', 1)
            if len(key_n_lefted) != 2:
                continue
            key, _ = key_n_lefted
            key = key.strip()
            if [key for p in params if key.startswith(p)]:
                continue
            item_list[index-1] = "{{ '%s' }}" % (item_list[index-1])

    after_data = ''.join(item_list)
    return after_data


def render(data, enable_tojson=True):
    if not isinstance(data, str):
        logger.warning(f'Format error! Expected str, found {type(data)}')
        return

    params = {
        'config': config,
        'ip': config.get('ip'),
        'port': config.get('mock.port'),
        'today': datetime.date.today(),
        'now':  datetime.datetime.now()
    }

    if enable_tojson:
        data = handle_jinja2_tojson_by_config(data)

    # Jinja2 doc
    # undefined and UndefinedError https://jinja.palletsprojects.com/en/3.1.x/api/#undefined-types
    # TemplateSyntaxError https://jinja.palletsprojects.com/en/3.1.x/api/#jinja2.TemplateSyntaxError

    try:
        template_data = Template(data, keep_trailing_newline=True, undefined=StrictUndefined)
        data = template_data.render(params)
    except (UndefinedError, TemplateSyntaxError):
        data = handle_jinja2_keywords(data, params)
        template_data = Template(data, keep_trailing_newline=True)
        data = template_data.render(params)
    except Exception:
        logger.error(f'Format error!\n {traceback.format_exc()}')

    return data


def get_query_array(url):
    # query string to array, example:
    # a=1&b=2 ==> ['a', '1', 'b', '2']
    # a=&b=2 ==> ['a', '', 'b', '2']
    # a&b=2 ==> ['a', '', 'b', '2']
    query_array = []
    qs_index = url.find('?')
    if qs_index < 0:
        return query_array

    query_string = url[qs_index+1:]
    if not query_string:
        return query_array

    for k_v in query_string.split('&'):
        if not k_v:
            continue

        k_v_item = k_v.split('=')
        if len(k_v_item) >= 2:
            query_array.extend(k_v_item[:2])
        else:
            query_array.extend([k_v, ''])
    return query_array


def url_decode(decode_obj, decode_key):
    if not isinstance(decode_obj, (dict, list)):
        return
    if isinstance(decode_obj, dict) and decode_key not in decode_obj:
        return
    if isinstance(decode_obj, list) and (not isinstance(decode_key, int) or decode_key >= len(decode_obj)):
        return
    url_decode_for_list_or_dict(decode_obj, decode_key)


def url_decode_for_list_or_dict(decode_obj, decode_key):
    if isinstance(decode_obj[decode_key], str):
        decode_obj[decode_key] = unquote(decode_obj[decode_key])
    elif isinstance(decode_obj[decode_key], list):
        for idx, _ in enumerate(decode_obj[decode_key]):
            url_decode(decode_obj[decode_key], idx)
    elif isinstance(decode_obj[decode_key], dict):
        for key, _ in decode_obj[decode_key].items():
            url_decode(decode_obj[decode_key], key)


def flow_str_2_data(data_str):
    if not isinstance(data_str, str):
        return data_str
    try:
        return json.loads(data_str)
    except Exception:
        return data_str


def flow_data_2_str(data):
    if isinstance(data, str):
        return data
    return json.dumps(data, ensure_ascii=False)


class CaseInsensitiveDict(dict):
    '''
    A dict data-structure that ignore key's case.
    Any read or write related operations will igonre key's case.

    Example:
    <key: 'abc'> & <key: 'ABC'> will be treated as the same key, only one exists in this dict.
    '''

    def __init__(self, raw_dict=None):
        self.__key_map = {}
        if raw_dict:
            for k, v in raw_dict.items():
                self.__setitem__(k, v)
    
    def __getstate__(self):
        return {
            'key_map': self.__key_map,
            'data': dict(self)
        }

    def __setstate__(self, state):
        self.__key_map = state['key_map']
        self.update(state['data'])

    def __get_real_key(self, key):
        return self.__key_map.get(key.lower(), key)

    def __set_real_key(self, real_key):
        if real_key.lower() not in self.__key_map:
            self.__key_map[real_key.lower()] = real_key

    def __pop_real_key(self, key):
        return self.__key_map.pop(key.lower())

    def __del_real_key(self, key):
        del self.__key_map[key.lower()]

    def __clear_key_map(self):
        self.__key_map.clear()

    def __setitem__(self, key, value):
        real_key = self.__get_real_key(key)
        self.__set_real_key(real_key)
        super(CaseInsensitiveDict, self).__setitem__(real_key, value)

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(self.__get_real_key(key))

    def get(self, key, default=None):
        return super(CaseInsensitiveDict, self).get(self.__get_real_key(key), default)

    def __delitem__(self, key):
        real_key = self.__pop_real_key(key)
        return super(CaseInsensitiveDict, self).__delitem__(real_key)

    def __contains__(self, key):
        return key.lower() in self.__key_map

    def pop(self, key):
        real_key = self.__pop_real_key(key)
        return super(CaseInsensitiveDict, self).pop(real_key)

    def popitem(self):
        item = super(CaseInsensitiveDict, self).popitem()
        if item:
            self.__del_real_key(item[0])
        return item

    def clear(self):
        self.__clear_key_map()
        return super(CaseInsensitiveDict, self).clear()

    def update(self, __m=None, **kwargs) -> None:
        if __m:
            for k, v in __m.items():
                self.__setitem__(k, v)
        if kwargs:
            for k, v in kwargs.items():
                self.__setitem__(k, v)

    def __reduce__(self):
        return (self.__class__, (dict(self),))


class HookedDict(dict):
    '''
    Hook build-in dict to protect CaseInsensitiveDict data type.
    Only <headers> value is CaseInsensitiveDict at present.
    '''

    def __init__(self, raw_dict):
        for k, v in raw_dict.items():
            if type(v) == dict:
                if k.lower() == 'headers':
                    v = CaseInsensitiveDict(v)
                else:
                    v = HookedDict(v)
            self.__setitem__(k, v)

    def __setitem__(self, __k, __v) -> None:
        if type(__v) == dict:
            if __k.lower() == 'headers':
                __v = CaseInsensitiveDict(__v)
            else:
                __v = HookedDict(__v)
        return super(HookedDict, self).__setitem__(__k, __v)

    def __reduce__(self):
        return (self.__class__, (dict(self),))


class TargetMatch:

    @staticmethod
    def is_match(target, pattern):
        if not TargetMatch._match_type(target, pattern):
            return False
        if type(target) == str:
            return TargetMatch._match_string(target, pattern)
        elif type(target) in [int, float]:
            return TargetMatch._match_numbers(target, pattern)
        elif type(target) == bool:
            return TargetMatch._match_boolean(target, pattern)
        elif type(target).__name__ == 'NoneType':
            return TargetMatch._match_null(target, pattern)
        else:
            logger.warning(f'Illegal match target type: {type(target)}')
            return False

    @staticmethod
    def _match_type(target, pattern):
        return isinstance(target, type(pattern))

    @staticmethod
    def _match_string(target, pattern):
        return True if re.search(pattern, target) else False

    @staticmethod
    def _match_numbers(target, pattern):
        return target == pattern

    @staticmethod
    def _match_boolean(target, pattern):
        return target == pattern

    @staticmethod
    def _match_null(target, pattern):
        return target == pattern


class JSONFormat:

    def json(self):
        prop_collection = {}
        props = dir(self)
        for prop in props:
            if prop.startswith('_'):
                continue
            prop_obj = getattr(self, prop)
            if isinstance(prop_obj, (str, int, bool, float)):
                prop_collection[prop] = prop_obj
            elif isinstance(prop_obj, datetime.datetime):
                prop_collection[prop] = prop_obj.timestamp()
        return prop_collection


class RedisManager:

    redis_dicts = set()

    @staticmethod
    def put(obj):
        RedisManager.redis_dicts.add(obj)

    @staticmethod
    def destory():
        for i in RedisManager.redis_dicts:
            i.destory()
        RedisManager.redis_dicts.clear()

    @staticmethod
    def serialize():
        return pickle.dumps(RedisManager.redis_dicts)

    @staticmethod
    def deserialize(data):
        RedisManager.redis_dicts = pickle.loads(data)


class RedisData:

    host = 'localhost'
    port = 6379
    db = 0

    def __init__(self, host=None, port=None, db=None, param_uuid=None):
        if not host:
            host = RedisData.host
        if not port:
            port = RedisData.port
        if not db:
            db = RedisData.db
        self.port = port
        self.host = host
        self.db = db
        if not param_uuid:
            self.uuid = str(uuid.uuid4())
        else:
            self.uuid = param_uuid
        self.redis = redis.Redis(host=self.host, port=self.port, db=self.db)
        RedisManager.put(self)

    def destory(self):
        self.redis.delete(self.uuid)
        self.redis.close()

    def copy(self):
        # Use the copy method with caution, especially during the create and release phases.
        return type(self)(host=self.host, port=self.port, db=self.db, param_uuid=self.uuid)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        if self.uuid != other.uuid:
            return False
        if self.host != other.host:
            return False
        if self.port != other.port:
            return False
        if self.db != other.db:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getstate__(self):
        return pickle.dumps({
            'uuid':self.uuid,
            'port':self.port,
            'host':self.host,
            'db':self.db
            })

    def __setstate__(self, state):
        data = pickle.loads(state)
        self.port = data['port']
        self.host = data['host']
        self.db = data['db']
        self.uuid = data['uuid']
        self.redis = redis.Redis(host=self.host, port=self.port, db=self.db)


class RedisDict(RedisData):

    def __init__(self, host=None, port=None, db=None, param_uuid=None, data={}):
        super().__init__(host, port, db, param_uuid)
        for k in data.keys():
            self[k] = data[k]

    def __getitem__(self, key):
        value = self.redis.hget(self.uuid, key)
        if value is None:
            raise KeyError(key)
        value = json.loads(value.decode())
        return _hook_value(self, key, value)

    def __setitem__(self, key, value):
        value = json.dumps(value, ensure_ascii=False)
        self.redis.hset(self.uuid, key, value)
        self.redis.expire(self.uuid, REDIS_EXPIRE_TIME)

    def __delitem__(self, key):
        if not self.redis.hexists(self.uuid, key):
            raise KeyError(key)
        self.redis.hdel(self.uuid, key)
        self.redis.expire(self.uuid, REDIS_EXPIRE_TIME)

    def __contains__(self, key):
        return self.redis.hexists(self.uuid, key)

    def __iter__(self):
        return self.raw()

    def keys(self):
        return [key.decode() for key in self.redis.hkeys(self.uuid)]

    def values(self):
        return [json.loads(value.decode()) for value in self.redis.hgetall(self.uuid).values()]

    def items(self):
        return [(key.decode(), json.loads(value.decode())) for key, value in self.redis.hgetall(self.uuid).items()]

    def get(self, key, default=None):
        value = self.redis.hget(self.uuid, key)
        if value is None:
            return default
        return _hook_value(self, key, json.loads(value.decode()))

    def update(self, data):
        for key, value in data.items():
            self[key] = value
        self.redis.expire(self.uuid, REDIS_EXPIRE_TIME)

    def pop(self, key, default=None):
        if key not in self:
            return default
        else:
            value = self.get(key, default)
            del self[key]
            return value

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def clear(self):
        self.redis.delete(self.uuid)

    def raw(self):
        return {key.decode(): json.loads(value.decode()) for key, value in self.redis.hgetall(self.uuid).items()}

    def __hash__(self):
        return hash((self.uuid, self.host, self.port, self.db))

    def __len__(self):
        return len(self.redis.hkeys(self.uuid))

    def __repr__(self):
        return repr(dict(self.items()))

    def __deepcopy__(self, memo):
        return self.raw()


def _hook_value(parent, key, value):
    if isinstance(value, dict):
        return RedisHookedDict(parent, key, value)
    elif isinstance(value, list):
        return RedisHookedList(parent, key, value)
    else:
        return value


class RedisHook:
    def __init__(self, parent, key):
        self.parent = parent
        self.key = key


class RedisHookedDict(RedisHook, dict):
    def __init__(self, parent, key, value):
        RedisHook.__init__(self, parent, key)
        dict.__init__(self, value)

    def get(self, key, default=None):
        res = dict.get(self, key, default)
        return _hook_value(self, key, res)

    def __getitem__(self, key):
        return _hook_value(self, key, dict.__getitem__(self, key))

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, _hook_value(self, key, value))
        self.parent[self.key] = self

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.parent[self.key] = self

    def update(self, *args, **kwargs):
        dict.update(self, *args, **kwargs)
        self.parent[self.key] = self

    def __deepcopy__(self, memo):
        return deepcopy(dict(self), memo)


class RedisHookedList(RedisHook, list):
    def __init__(self, parent, key, value):
        list.__init__(self, value)
        RedisHook.__init__(self, parent, key)

    def __getitem__(self, index):
        return _hook_value(self, index, list.__getitem__(self, index))

    def __setitem__(self, index, value):
        list.__setitem__(self, index, _hook_value(self, index, value))
        self.parent[self.key] = self

    def __delitem__(self, index):
        list.__delitem__(self, index)
        self.parent[self.key] = self

    def append(self, value):
        list.append(self, value)
        self.parent[self.key] = self

    def __deepcopy__(self, memo):
        return deepcopy(list(self), memo)
