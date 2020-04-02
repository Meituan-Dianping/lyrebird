from .gzip import GzipHandler
from .default import DefaultHandler

content_encoding_handlers = {
    'gzip': GzipHandler,
}

def _get_matched_action(content_encoding_name):
    if content_encoding_name in content_encoding_handlers:
        return content_encoding_handlers[content_encoding_name]
    return DefaultHandler

def origin2flow(content_encoding, request_data):
    func = _get_matched_action(content_encoding)
    _data = func.origin2flow(request_data)
    return _data

def flow2origin(content_encoding, flow_data):
    func = _get_matched_action(content_encoding)
    _data = func.flow2origin(flow_data)
    return _data
