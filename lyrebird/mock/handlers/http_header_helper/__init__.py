from collections import OrderedDict
from .content_length import ContentLengthHandler
from ..duplicate_header_key_handler import DuplicateHeaderKeyHandler
from lyrebird.utils import CaseInsensitiveDict

origin2flow_handlers = OrderedDict({
})

flow2origin_handlers = OrderedDict({
    'Content-Length': ContentLengthHandler
})


class HeadersHelper:

    @staticmethod
    def origin2flow(origin_obj, output=None):
        _origin_headers = origin_obj.headers
        if not _origin_headers:
            return

        _headers = DuplicateHeaderKeyHandler.origin2flow(_origin_headers)

        for headers_key, func in origin2flow_handlers.items():
            _headers[headers_key] = func.flow2origin(origin_obj)

        if output:
            output['headers'] = _headers
        else:
            return _headers

    @staticmethod
    def flow2origin(flow_obj, output=None, chain=None):
        _headers = flow_obj.get('headers')
        if not _headers:
            return

        for headers_key, func in flow2origin_handlers.items():
            _headers[headers_key] = func.flow2origin(flow_obj, chain=chain)

        if output:
            output.headers = _headers
        else:
            return _headers

    @staticmethod
    def get_raw_headers(origin_request):
        raw_headers = {}
        if '_raw_header' in origin_request.environ:
            raw_headers = CaseInsensitiveDict(origin_request.environ['_raw_header'])
            for key in ('cache-control', 'host', 'transfer-encoding', 'lyrebird-client-address'):
                if key in raw_headers:
                    del raw_headers[key]
        return raw_headers
