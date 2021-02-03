"""
Script for mitmdump

Redirect request from proxy server to mock server
"""

from mitmproxy import http
from lyrebird import log
import os
import json
import logging
import re

_logger = log.get_logger()
_logger.setLevel(logging.INFO)

PROXY_PORT = int(os.environ.get('PROXY_PORT'))
PROXY_FILTERS = json.loads(os.environ.get('PROXY_FILTERS'))

def to_mock_server(flow: http.HTTPFlow):
    # mock path 为/mock开头加上原始url
    flow.request.path = '/mock/' + flow.request.url
    # mock scheme 统一为http
    flow.request.scheme = 'http'
    # mock server port
    flow.request.port = PROXY_PORT
    # mock server ip
    flow.request.host = '127.0.0.1'
    # device real ip
    address = flow.client_conn.address[0]
    # 获取的address是IPv6（内嵌IPv4地址表示法），需要获取IPv4地址，需要做以下处理
    if address.startswith('::ffff:'):
        address = address.split('::ffff:')[1]
    flow.request.headers['Lyrebird-Client-Address'] = address
    _logger.info('Redirect-> %s' % flow.request.url[:100])


def request(flow: http.HTTPFlow):
    _logger.info(flow.request.url[:100])
    
    if not PROXY_FILTERS:
        to_mock_server(flow)
        return

    for _filter in PROXY_FILTERS:
        if re.search(_filter, flow.request.url):
            to_mock_server(flow)
            break


def responseheaders(flow):
    """
    Enables streaming for all responses.
    This is equivalent to passing `--set stream_large_bodies=1` to mitmproxy.
    """
    if 'mitm.it' in flow.request.url:
        # Support mitm.it
        flow.response.stream = False
        return
    flow.response.stream = True
