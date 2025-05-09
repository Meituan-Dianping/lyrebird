from .gzip import GzipHandler
from .default import DefaultHandler
from .br import BrotliHandler
from .zstd import ZstdHandler
from lyrebird.log import get_logger

logger = get_logger()

content_encoding_handlers = {
    'gzip': GzipHandler,
    'br': BrotliHandler,
    'zstd': ZstdHandler,
}

def _get_matched_action(content_encoding_name):
    if content_encoding_name in content_encoding_handlers:
        return content_encoding_handlers[content_encoding_name]
    return DefaultHandler

def origin2flow(content_encoding, request_data, chain=None):
    func = _get_matched_action(content_encoding)
    try:
        _data = func.origin2flow(request_data)
    except Exception as e:
        func = DefaultHandler
        _data = func.origin2flow(request_data)
        logger.warning(f'Convert Content-Encoding: {content_encoding} data origin2flow failed! {e}')
    finally:
        if chain and isinstance(chain, list):
            chain.append(func)

    return _data

def flow2origin(content_encoding, flow_data):
    func = _get_matched_action(content_encoding)
    try:
        _data = func.flow2origin(flow_data)
    except Exception as e:
        _data = DefaultHandler.flow2origin(flow_data)
        logger.warning(f'Convert Content-Encoding: {content_encoding} data flow2origin failed! {e}')
    return _data

def origin2string(content_encoding, request_data):
    func = _get_matched_action(content_encoding)
    try:
        _data = func.origin2string(request_data)
    except Exception as e:
        func = DefaultHandler
        _data = func.origin2string(request_data)
        logger.warning(f'Convert Content-Encoding: {content_encoding} data origin2string failed! {e}')

    return _data
