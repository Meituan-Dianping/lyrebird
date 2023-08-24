import re
import platform
from packaging import version
from lyrebird.log import get_logger

logger = get_logger()


class JSONPath:

    @staticmethod
    def search(root, path:str, find_one=False):
        """ Find JSON object in object (a ``list`` or ``dict`` JSON object) file by JSONPath

        ``root`` <list> or <dict> an object containing data

        ``path`` <str> describe JSONPath of the target data, and must follow rules:
        1. Start with `$`
        2. Fuzzy search is not supported

        """

        if not path or not isinstance(path, str) or not isinstance(root, (list, dict)):
            return

        if path.startswith('$'):
            path = path.replace('$', '', 1)

        # split by `.` and drop `.`, split by `[ ]` and keep `[ ]`
        # EXAMPLE
        # path = 'data[*][1].name'
        # keys = ['data', '[*]', '[1]', 'name']

        pattern = r'(?:\.)|(?=\[.*\])'
        origin_keys = re.split(pattern, path)

        # There is a bug in re.split splitting with (?=) in Python 3.6 and below
        # The following code `re_split_handle` is used to solve this problem
        # Remove when Python 3.6 is not supported
        keys = [k for k in JSONPath.re_split_handle(origin_keys) if k]

        if not keys or not len(keys):
            return

        result = []
        JSONPath._search_iterator(root, keys, result)
        if find_one:
            return result[0].node if result else None
        return result

    @staticmethod
    def re_split_handle(origin_keys):
        # EXAMPLE
        # origin_keys = ['data[*][1]', 'name']
        # return keys = ['data', '[*]', '[1]', 'name']
        if version.parse(platform.python_version()) >= version.parse('3.7.0'):
            return origin_keys

        keys = []
        for key in origin_keys:
            keys.extend(re.findall('\[?[\w\*]+\]?', key))
        return keys

    @staticmethod
    def _search_iterator(root, prop_keys, result):
        current_key = prop_keys[0]

        keys = JSONPath.get_target_keys(root, current_key)
        for key in keys:
            if len(prop_keys) == 1:
                result.append(Node(root, key))
            else:
                JSONPath._search_iterator(root[key], prop_keys[1:], result)

    @staticmethod
    def get_target_keys(root, key):
        # EXAMPLE
        # matched [0], [10], [*]
        is_list = re.match('\[(\d+|\*)\]', key)

        if not is_list:
            if isinstance(root, dict) and (key in root):
                return (key,)
            else:
                return ()

        index = key.strip('[').strip(']')
        if not isinstance(root, list):
            return ()
        if index == '*':
            return range(0, len(root))
        if index.isdigit() and int(index) < len(root):
            return (int(index),)

        return ()


class Node:
    def __init__(self, parent, key):
        self.parent = parent
        self.node = parent[key]
        self.key = key

jsonpath = JSONPath()
