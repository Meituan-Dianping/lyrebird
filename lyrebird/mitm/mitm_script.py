"""
Script for mitmdump

Redirect request from proxy server to mock server
"""
import os
import json
from mitmproxy import http
from urllib.parse import urlparse


SERVER_IP = os.environ.get('SERVER_IP')
MOCK_PORT = int(os.environ.get('MOCK_PORT'))
PROXY_PORT = int(os.environ.get('PROXY_PORT'))
PROXY_FILTERS = json.loads(os.environ.get('PROXY_FILTERS'))


def is_websocket_request(flow: http.HTTPFlow) -> bool:
    headers = flow.request.headers
    return (
        headers.get('Upgrade', '').lower() == 'websocket' and
        headers.get('Connection', '').lower() == 'upgrade'
    )


def check_lyrebird_request(flow: http.HTTPFlow):
    parsed_url = urlparse(flow.request.url)
    host = parsed_url.hostname
    port = parsed_url.port
    if host not in ('localhost', '127.0.0.1', SERVER_IP):
        return False
    if not port or port not in (MOCK_PORT, PROXY_PORT):
        return False
    return True


def to_mock_server(flow: http.HTTPFlow):
    raw_url = urlparse(flow.request.url)
    raw_host = raw_url.hostname
    if raw_url.port:
        raw_host += f':{raw_url.port}'
    # mock path 为/mock开头加上原始url
    flow.request.path = '/' + flow.request.url
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
    flow.request.headers['Proxy-Raw-Headers'] = json.dumps({name: flow.request.headers[name]
                                                           for name in flow.request.headers if name.lower() not in ('host', 'proxy-raw-headers')}, ensure_ascii=False)


def request(flow: http.HTTPFlow):
    if 'mitm.it' in flow.request.url:
        # Support mitm.it
        return
    if check_lyrebird_request(flow):
        # Avoid internal requests
        return
    if is_websocket_request(flow):
        # Avoid Websocket connect requests
        return
    to_mock_server(flow)


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
