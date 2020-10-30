import re
from lyrebird.log import get_logger

logger = get_logger()


class Jsonpath:
    def __init__(self):
        self.DICT_SPLIT = '.'
        self.PATH_ROOT = '$'
        self.result = []

    def search(self, root, path:str):
        """ Find JSON object in object (a ``list`` or ``dict`` JSON object) file by jsonpath

        ``root`` <list> or <dict> an object containing data

        ``jsonpath`` <str> describe jsonpath of the target data, and must follow rules:
        1. Start with `$`
        2. Fuzzy search is not supported

        """

        self.result = []
        if not path or not isinstance(path, str) or not isinstance(root, (list, dict)):
            return

        # split by `.` and drop `.`, split by `[ ]` and keep `[ ]`
        # EXAMPLE
        # path = '$.data[0][1].name'
        # keys = ['$', 'data', '[0]', '[1]', 'name']
        pattern = r'(?:\.)|(?=\[.*\])'
        keys = re.split(pattern, path)

        if keys[0] != self.PATH_ROOT:
            logger.warning(f'jsonpath error! Jsonpath {path} does not start with `$` or `$[*]`!')
            return

        self._jsonpath_iterator(root, keys[1:])
        return self.result

    def _jsonpath_iterator(self, root, prop_keys):
        current_key = prop_keys[0]

        keys = self.get_target_keys(root, current_key)
        for key in keys:
            self._collect_result(root, key) if len(prop_keys) == 1 else self._jsonpath_iterator(root[key], prop_keys[1:])

    @staticmethod
    def is_key_list(key): # new
        # EXAMPLE
        # [0], [10], [*]
        pattern = '\[(\d+|\*)\]'
        res = re.match(pattern, key)
        return res

    @staticmethod
    def get_target_keys(root, key): # new
        is_list = Jsonpath.is_key_list(key)

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

    def _collect_result(self, parent, key):
        node = Node(parent, key)
        self.result.append(node)


class Node:
    def __init__(self, parent, key):
        self.parent = parent
        self.node = parent[key]
        self.key = key

jsonpath = Jsonpath()
