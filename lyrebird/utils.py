import re
import os
import math
import time
import socket
import tarfile
import requests
import datetime
import netifaces
import traceback
from pathlib import Path
from jinja2 import Template
from contextlib import closing
from lyrebird.log import get_logger
from lyrebird.application import config

logger = get_logger()


def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


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


def render_data_with_tojson(data):
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
        data = render_data_with_tojson(data)
    data = handle_jinja2_keywords(data, params)

    try:
        template_data = Template(data, keep_trailing_newline=True)
        return template_data.render(params)
    except Exception:
        logger.error(f'Format error!\n {traceback.format_exc()}')
        return data


def get_query_array(url):
    # query string to array
    # like a=1&b=2 ==> [a, 1, b, 2]
    query_array = []
    qs_index = url.find('?')
    if qs_index >= 0:
        query_string = url[qs_index+1:]
        query_array = re.split('\\&|\\=', query_string)
    return query_array


class CaseInsensitiveDict(dict):
    '''
    A dict data-structure that ignore key's case.
    Any read or write related operations will igonre key's case.

    Example:
    <key: 'abc'> & <key: 'ABC'> will be treated as the same key, only one exists in this dict.
    '''

    def __init__(self, raw_dict):
        self.__key_map = {}
        for k, v in raw_dict.items():
            self.__setitem__(k, v)

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
