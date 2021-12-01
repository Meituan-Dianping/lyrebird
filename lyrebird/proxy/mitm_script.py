"""
Script for mitmdump

Redirect request from proxy server to mock server
"""

from urllib.parse import urlparse
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
    raw_url = urlparse(flow.request.url)
    raw_host = raw_url.hostname
    if raw_url.port:
        raw_host += f':{raw_url.port}'
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
    flow.request.headers['Mitmproxy-Proxy'] = address
    # 获取原始的请求host，加入Header key:Host, 用于重定向
    flow.request.headers['Host'] = raw_host
    flow.request.headers['Proxy-Raw-Headers'] = json.dumps({name: flow.request.headers[name] for name in flow.request.headers}, ensure_ascii=False)

    _logger.info('Redirect-> %s' % flow.request.url[:100])


def request(flow: http.HTTPFlow):
    _logger.info(flow.request.url[:100])
    if 'mitm.it' in flow.request.url:
        # Support mitm.it
        return

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

    command = flow.response.headers.get('Lyrebird-Mitmproxy-Command')
    if command == 'kill':
        flow.kill()
    _recover_response_header_location(flow.response.headers)


def _recover_response_header_location(response_header):
    """
        Recover response header key <Location>’s raw value for redirect against cookie missing.
    """
    raw_location = response_header.get('Raw-Location')
    if raw_location:
        response_header.update({'Location': raw_location})
        response_header.pop('Raw-Location')
