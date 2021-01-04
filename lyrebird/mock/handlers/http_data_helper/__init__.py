from collections import OrderedDict
from . import content_encoding, content_type

origin2flow_handlers = OrderedDict({
    'Content-Encoding': content_encoding,
    'Content-Type': content_type
})

flow2origin_handlers = OrderedDict({
    'Content-Type': content_type,
    'Content-Encoding': content_encoding
})


class DataHelper:

    @staticmethod
    def origin2flow(origin_obj, output=None):
        _data = origin_obj.data
        if not _data:
            return

        for headers_key, func in origin2flow_handlers.items():
            headers_val = origin_obj.headers.get(headers_key, '')
            _data = func.origin2flow(headers_val, _data)

        if output:
            output['data'] = _data
        else:
            return _data

    @staticmethod
    def flow2origin(flow_obj, output=None):
        _data = flow_obj.get('data')
        if not _data:
            return

        for headers_key, func in flow2origin_handlers.items():
            headers_val = flow_obj['headers'].get(headers_key, '')
            _data = func.flow2origin(headers_val, _data)

        if output:
            output.data = _data
        else:
            return _data
