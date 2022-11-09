from aiohttp import web, client
from typing import List, Set, Optional
from urllib import parse as urlparse
import re


class UnknownLyrebirdProxyProtocol(Exception):
    pass


class LyrebirdProxyContext:
    def __init__(self):
        self.request: web.Request = None
        self.netloc = None
        self.origin_url = None
        self.forward_url = None
        self.init = False
        self.protocol_parsers = [
            self.protocol_read_from_path,
            self.protocol_read_from_header,
            self.protocol_read_from_query,
            self.protocol_read_from_query_2
        ]

    def protocol_read_from_path(self, request: web.Request, lb_config):
        # Lyrebird proxy protocol #1
        # Origin target info in path
        # e.g.
        # http://{lyrebird_host}/{origin_full_url}

        if not request.path.startswith('/http://') and not request.path.startswith('/https://'):
            return

        origin_full_url = request.path_qs[1:]
        url = urlparse.urlparse(origin_full_url)

        # origin url for proxy
        self.origin_url = origin_full_url
        # forward url to lyrebird main port 'default 9090'
        port = lb_config.get('mock.port')
        self.forward_url = f'http://127.0.0.1:{port}/mock/{origin_full_url}'

        self.netloc = url.netloc
        self.request = request

        # Set init success
        self.init = True

    def protocol_read_from_header(self, request: web.Request, lb_config):
        # Lyrebird proxy protocol #2
        # Origin target info in headers
        # e.g.
        # http://{lyrebird_host}/{origing_path_and_query}
        # headers:
        # MKScheme: {origin_scheme}
        # MKOriginHost: {origin_host}
        # MKOriginPort: {origin_port}
        header_name_scheme = lb_config.get('mock.proxy_headers', {}).get('scheme')
        header_name_host = lb_config.get('mock.proxy_headers', {}).get('host')
        header_name_port = lb_config.get('mock.proxy_headers', {}).get('port')

        if not request.headers.get(header_name_host) or not request.headers.get(header_name_scheme):
            return

        target_scheme = request.headers.get(header_name_scheme)
        target_host = request.headers.get(header_name_host)
        target_port = request.headers.get(header_name_port)
        if target_port:
            origin_full_url = f'{target_scheme}://{target_host}:{target_port}{request.rel_url}'
            netloc = f'{target_host}:{target_port}'
        else:
            origin_full_url = f'{target_scheme}://{target_host}{request.rel_url}'
            netloc = target_host

        # origin url for proxy
        self.origin_url = origin_full_url
        # forward url to lyrebird main port 'default 9090'
        port = lb_config.get('mock.port')
        self.forward_url = f'http://127.0.0.1:{port}/mock/{origin_full_url}'
        self.netloc = netloc
        self.request = request

        # Set init success
        self.init = True

    def protocol_read_from_query(self, request: web.Request, lb_config):
        # Lyrebird proxy protocol #3
        # Origin target info in query
        # key is "proxy"
        # e.g.
        # http://{lyrebird_host}/{origing_path}?{proxy=encoded-url}

        # default key=proxy
        if not request.query.get('proxy'):
            return

        origin_url = request.query.get('proxy')
        origin_url = urlparse.unquote(origin_url)
        url = urlparse.urlparse(origin_url)

        self.origin_url = origin_url
        # forward url to lyrebird main port 'default 9090'
        port = lb_config.get('mock.port')
        self.forward_url = f'http://127.0.0.1:{port}/mock/?proxy={urlparse.quote(origin_url)}'
        self.netloc = url.netloc
        self.request = request

        # Set init success
        self.init = True

    def protocol_read_from_query_2(self, request: web.Request, lb_config):
        # Lyrebird proxy protocol #4
        # Origin target info in query
        # Set proxyscheme、proxyhost、proxypath
        # e.g.
        # http://{lyrebird_host}?proxyscheme={origin_scheme}&proxyhost={urlencode(origin_host)}&proxypath={urlencode(origin_path)}&{origin_query}
        proxy_scheme = request.query.get('proxyscheme', 'http')
        proxy_host = request.query.get('proxyhost', None)
        proxy_path = request.query.get('proxypath', '/')

        if not proxy_host:
            return

        origin_query_str = ''
        qs_index = request.path_qs.find('?')
        if qs_index >= 0:
            # query string to 2D array
            # like a=1&b=2 ==> [(a, 1), (b, 2)]
            raw_query_string = request.path_qs[qs_index+1:]
            raw_query_array = re.split('\\&|\\=', raw_query_string)
            raw_query_items = list(zip(raw_query_array[::2], raw_query_array[1::2]))
            # remove lyrebrid proxy protocol keys from query string
            raw_query_items = list(filter(lambda x: x[0] not in ['proxyscheme',
                                   'proxyhost', 'proxypath'], raw_query_items))
            # 2D array to query string
            origin_query_str = '?'+'&'.join([f'{item[0]}={item[1]}' for item in raw_query_items])

        origin_url = f'{proxy_scheme}://{urlparse.unquote(proxy_host)}{urlparse.unquote(proxy_path)}{origin_query_str}'

        self.origin_url = origin_url
        url = urlparse.urlparse(origin_url)

        # forward url to lyrebird main port 'default 9090'
        port = lb_config.get('mock.port')
        self.forward_url = f'http://127.0.0.1:{port}/mock/{origin_url}'
        self.netloc = url.netloc
        self.request = request

        # Set init success
        self.init = True

    @classmethod
    def parse(cls, request: web.Request, lb_config):
        ctx = cls()
        for parser in ctx.protocol_parsers:
            parser(request, lb_config)
            if ctx.init:
                return ctx
        raise UnknownLyrebirdProxyProtocol
