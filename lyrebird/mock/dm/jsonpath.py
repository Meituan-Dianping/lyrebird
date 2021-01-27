import re
from lyrebird.log import get_logger

logger = get_logger()


class JSONPath:

    @staticmethod
    def search(root, path:str):
        """ Find JSON object in object (a ``list`` or ``dict`` JSON object) file by JSONPath

        ``root`` <list> or <dict> an object containing data

        ``path`` <str> describe JSONPath of the target data, and must follow rules:
        1. Start with `$`
        2. Fuzzy search is not supported

        """

        if not path or not isinstance(path, str) or not isinstance(root, (list, dict)):
            return

        if path.startswith('$.'):
            path = path.replace('$.', '', 1)

        # split by `.` and drop `.`, split by `[ ]` and keep `[ ]`
        # EXAMPLE
        # path = 'data[0][1].name'
        # keys = ['data', '[0]', '[1]', 'name']

        pattern = r'(?:\.)|(?=\[.*\])'
        keys = re.split(pattern, path)
        if not keys or not len(keys):
            return

        result = []
        JSONPath._search_iterator(root, keys, result)
        return result

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
            if isinstance(root, dict) and root.get(key):
                return (key,)
            else:
                return ()

        index = key.strip('[').strip(']')
        if not isinstance(root, list):
            return ()
        if index == '*':
            return range(0, len(root))
        if index.isdigit() and int(index) < len(root) - 1:
            return (int(index),)

        return ()


class Node:
    def __init__(self, parent, key):
        self.parent = parent
        self.node = parent[key]
        self.key = key

jsonpath = JSONPath()
