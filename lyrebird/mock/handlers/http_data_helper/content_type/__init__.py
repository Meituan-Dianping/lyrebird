from .form import FormHandler
from .json import JsonHandler
from .text import TextHandler
from .default import DefaultHandler

_content_type_map = {
    'application/x-www-form-urlencoded': FormHandler,
    'application/json': JsonHandler,
    'text/': TextHandler
}

def _get_matched_action(content_type):
    for pattern, func in _content_type_map.items():
        if content_type.startswith(pattern):
            return func
    return DefaultHandler

def origin2flow(content_type, request_data):
    func = _get_matched_action(content_type)
    _data = func.origin2flow(request_data)
    return _data

def flow2origin(content_type, flow_data):
    func = _get_matched_action(content_type)
    _data = func.flow2origin(flow_data)
    return _data
