from .form import FormHandler
from .json import JsonHandler
from .text import TextHandler
from .javascript import JavascriptHandler
from .default import DefaultHandler
from lyrebird.log import get_logger

logger = get_logger()

content_type_handlers = {
    'application/x-www-form-urlencoded': FormHandler,
    'application/javascript': JavascriptHandler,
    'application/json': JsonHandler,
    'text/': TextHandler
}

def _get_matched_action(content_type):
    for pattern, func in content_type_handlers.items():
        if content_type.startswith(pattern):
            return func
    return DefaultHandler

def origin2flow(content_type, request_data, chain=None):
    func = _get_matched_action(content_type)
    try:
        _data = func.origin2flow(request_data)
    except Exception as e:
        func = DefaultHandler
        _data = func.origin2flow(request_data)
        logger.warning(f'Convert Content-Type: {content_type} data origin2flow failed! {e}')
    finally:
        chain.append(func)

    return _data

def flow2origin(content_type, flow_data):
    func = _get_matched_action(content_type)
    try:
        _data = func.flow2origin(flow_data)
    except Exception as e:
        _data = DefaultHandler.flow2origin(flow_data)
        logger.warning(f'Convert Content-Type: {content_type} data flow2origin failed! {e}')
    return _data
