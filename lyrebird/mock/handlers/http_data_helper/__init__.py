from collections import OrderedDict
from . import content_encoding, content_type
import json

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
        if not origin_obj:
            return

        _data = origin_obj.data
        if not _data:
            return

        # Read raw headers, support the request from extra mock 9999 port
        if 'Proxy-Raw-Headers' in origin_obj.headers:
            _origin_headers = json.loads(origin_obj.headers['Proxy-Raw-Headers'])
            raw_headers = _origin_headers
        else:
            raw_headers = origin_obj.headers

        for headers_key, func in origin2flow_handlers.items():
            headers_val = raw_headers.get(headers_key, '')
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
