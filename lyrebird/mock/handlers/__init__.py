from . import mock_handler, path_not_found_handler, proxy_handler
from collections import OrderedDict


def get_inner_handlers():
    return OrderedDict(
        {
            'mock': mock_handler.MockHandler(),
            'proxy': proxy_handler.ProxyHandler(),
            '404': path_not_found_handler.RequestPathNotFound()
        }
    )
