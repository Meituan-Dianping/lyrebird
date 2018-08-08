from mitmproxy import http
from lyrebird import application
from lyrebird.mock.logger_helper import get_logger

"""
Script for mitmdump

Redirect request from proxy server to mock server
"""

_log = get_logger()


def to_mock_server(flow: http.HTTPFlow):
    conf = application.config
    # mock path 为/mock开头加上原始url
    flow.request.path = '/mock/' + flow.request.url
    # mock scheme 统一为http
    flow.request.scheme = 'http'
    # mock server port
    flow.request.port = conf.get('mock.port')
    # mock server ip
    flow.request.host = conf.get('mock.host', 'localhost')
    # device real ip
    flow.request.headers['lyrebird.device.ip'] = flow.client_conn.address[0]
    _log.info('Redirect-> %s' % flow.request.url[:100])


def request(flow: http.HTTPFlow):
    conf = application.config
    _log.info(flow.request.url[:100])
    filters = conf.get('proxy.filters')
    if not filters:
        to_mock_server(flow)
        return
    for _filter in filters:
        if _filter in flow.request.host:
            to_mock_server(flow)
            break
