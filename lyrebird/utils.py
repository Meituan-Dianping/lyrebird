import re
import os
import math
import time
import socket
import tarfile
import requests
from pathlib import Path
from contextlib import closing
from lyrebird.log import get_logger

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


def is_target_match_patterns(pattern_list, target):
    if not pattern_list or not target:
        return False
    for pattern in pattern_list:
        if TargetMatch.is_match(target, pattern):
            return True
    return False


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


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


class CaseInsensitiveDict(dict):

    def __init__(self, dict):
        for k,v in dict.items():
            self.__setitem__(k, v)

    def __setitem__(self, key, value):
        super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super(CaseInsensitiveDict, self).__getitem__(key.lower())
    
    def get(self, key, default=None):
        return super(CaseInsensitiveDict, self).get(key.lower(), default)

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
