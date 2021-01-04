import uuid
import time
import ipaddress

from .. import context
from lyrebird import utils
from lyrebird import application
from lyrebird.log import get_logger
from lyrebird.mock.blueprints.apis.bandwidth import config
from urllib.parse import urlparse, unquote
from .http_data_helper import DataHelper
from .http_header_helper import HeadersHelper


logger = get_logger()


class HandlerContext:
    """
    请求处理器上下文变量
    用于保存一个请求处理过程中的request, response

    """
    MOCK_PATH_PREFIX = '/mock'

    def __init__(self, request):
        self.id = str(uuid.uuid4())
        self.request = request
        self.response = None
        self.client_req_time = None
        self.client_resp_time = None
        self.server_req_time = None
        self.server_resp_time = None
        self.flow = dict(
            id=self.id,
            size=0,
            duration=0,
            start_time=time.time(),
            request={},
            response={}
            )
        self.client_address = None
        self.is_request_edited = False
        self.is_response_edited = False
        self.response_source = ''
        self.is_proxiable = True
        self.response_chunk_size = 2048
        self._parse_request()

    def _parse_request(self):
        # Read stream
        self.request.get_data()
        # parse path
        request_info = self._read_origin_request_info_from_url()
        if not request_info['host']:
            request_info_from_header = self._read_origin_request_info_from_header()
            if len(request_info_from_header) > 0:
                request_info = request_info_from_header

        headers = HeadersHelper.origin2flow(self.request)
        _request = dict(
            headers=headers,
            method=self.request.method,
            query=self.request.args,
            timestamp=round(time.time(), 3)
        )
        _request.update(request_info)

        # handle request data
        if self.request.method in ['POST', 'PUT']:
            DataHelper.origin2flow(self.request, output=_request)

        if self.request.headers.get('Lyrebird-Client-Address'):
            self.client_address = self.request.headers.get('Lyrebird-Client-Address')
        else:
            self.client_address = self.request.remote_addr
        self.flow['client_address'] = self.client_address

        self.flow['request'] = _request
        context.application.cache.add(self.flow)

        logger.debug(f'[On client request] {self.flow["request"]["url"]}')

    def _read_origin_request_info_from_url(self):
        url_prefix = '/'+self.request.blueprint+'/'
        raw_url = self.request.path[len(url_prefix):]
        if self.request.query_string:
            raw_url += '?' + self.request.query_string.decode()
        parsed_path = urlparse(raw_url)
        # urllib.unquote : fix bug - url contains ',' will be auto encoded by flask, that cause proxy not work.
        # e.g /1.2,3 -> 1.2%2C3
        _request = dict(
            url=raw_url,
            scheme=parsed_path.scheme,
            host=parsed_path.hostname,
            port=parsed_path.port if parsed_path.port else '80',
            path=unquote(parsed_path.path)
        )
        return _request

    def _read_origin_request_info_from_header(self):
        proxy_headers = application.config['mock.proxy_headers']
        scheme = self.request.headers.get(proxy_headers['scheme'], default='http')
        host = self.request.headers.get(proxy_headers['host'])
        port = self.request.headers.get(proxy_headers['port'], default='80')
        if not host:
            return {}
        scheme = scheme.strip()
        host = host.strip()
        port = port.strip()
        # if host is IP address then full_host=host:port
        # else if is a domain the full_host=host
        full_host = host
        try:
            ipaddress.ip_address(host)
            full_host = host + ':' + port
        except Exception:
            pass
        return dict(
            url=scheme+'://'+full_host+self.request.full_path[len(self.MOCK_PATH_PREFIX):],
            scheme=scheme,
            host=host,
            port=port,
            path=self.request.path[len(self.MOCK_PATH_PREFIX):]
        )

    def set_request_edited(self):
        self.is_request_edited = True

    def set_response_edited(self):
        self.is_response_edited = True

    def set_response_source_mock(self):
        self.response_source = 'mock'

    def set_response_source_proxy(self):
        self.response_source = 'proxy'

    def get_request_body(self):
        if self.is_request_edited:
            self.flow['request']['headers'] = HeadersHelper.flow2origin(self.flow['request'])
            _data = DataHelper.flow2origin(self.flow['request'])
        else:
            _data = self.request.data or self.request.form or None
        return _data

    def get_request_headers(self):
        if self.is_request_edited:
            self.flow['request']['headers'] = HeadersHelper.flow2origin(self.flow['request'])

        headers = {}
        unproxy_headers = application.config.get('proxy.ignored_headers', {})
        for name, value in self.flow['request']['headers'].items():
            if not value or name in ['Cache-Control', 'Host']:
                continue
            if name in unproxy_headers and unproxy_headers[name] in value:
                continue
            headers[name] = value
        return headers

    def get_response_generator(self):
        if self.is_response_edited:
            self.flow['response']['headers'] = HeadersHelper.flow2origin(self.flow['response'])
            _generator = self._generator_bytes()
        else:
            _generator = self._generator_stream()
        return _generator

    def _generator_bytes(self):
        def generator():
            try:
                _resp_data = DataHelper.flow2origin(self.flow['response']) or ''
                length = len(_resp_data)
                size = self.response_chunk_size
                bandwidth = config.bandwidth
                if bandwidth > 0:
                    sleep_time = self.response_chunk_size / (bandwidth * 1024)
                else:
                    sleep_time = 0
                for i in range(int(length/size) + 1):
                    time.sleep(sleep_time)
                    self.server_resp_time = time.time()
                    yield _resp_data[ i * size : (i+1) * size ]
            finally:
                self.update_client_resp_time()
        return generator

    def _generator_stream(self):
        def generator():
            upstream = self.response
            try:
                bandwidth = config.bandwidth
                if bandwidth > 0:
                    sleep_time = self.response_chunk_size / (bandwidth * 1024)
                else:
                    sleep_time = 0
                buffer = []
                for item in upstream.response:
                    buffer.append(item)
                    time.sleep(sleep_time)
                    self.server_resp_time = time.time()
                    yield item
            finally:
                self.response.data = b''.join(buffer)
                DataHelper.origin2flow(self.response, output=self.flow['response'])

                self.update_client_resp_time()
                upstream.close()
        return generator

    def update_response_headers_code2flow(self, output_key='response'):
        self.flow[output_key]  = {
            'code': self.response.status_code,
            'timestamp': round(time.time(), 3)
        }
        HeadersHelper.origin2flow(self.response, output=self.flow[output_key])

    def update_response_data2flow(self, output_key='response'):
        DataHelper.origin2flow(self.response, output=self.flow[output_key])

    def update_client_req_time(self):
        self.client_req_time = time.time()
        # 消息总线 客户端请求事件，启用此事件
        method = self.flow['request']['method']
        url = self.flow['request']['url']

        _flow_client_req = {}
        for key, value in self.flow.items():
            _flow_client_req[key] = value

        context.application.event_bus.publish(
            'flow.request',
            dict(
                flow=_flow_client_req,
                message=f"URL: {url}\nMethod: {method}\n"
            )
        )

    def update_client_resp_time(self):
        self.client_resp_time = time.time()
        # 消息总线 客户端响应事件，启用此事件
        resp_data = self.flow['response'].get('data', '')
        if isinstance(resp_data, str):
            self.flow['size'] = len(resp_data.encode())
        else:
            self.flow['size'] = len(resp_data)

        self.flow['duration'] = self.server_resp_time - self.client_req_time

        method = self.flow['request']['method']
        url = self.flow['request']['url']
        code = self.flow['response']['code']
        duration = utils.convert_time(self.flow['duration'])
        size = utils.convert_size(self.flow['size'])

        # Import decoder for decoding the requested content
        decode_flow = {}
        application.encoders_decoders.decoder_handler(self.flow, output=decode_flow)

        context.application.event_bus.publish(
            'flow',
            dict(
                flow=decode_flow,
                message=f"URL: {url}\nMethod: {method}\nStatusCode: {code}\nDuration: {duration}\nSize: {size}"
            )
        )

        if context.application.work_mode == context.Mode.RECORD:
            dm = context.application.data_manager
            dm.save_data(self.flow)

    def update_server_req_time(self):
        self.server_req_time = time.time()
        # 消息总线 向服务端转发请求事件，暂不使用
        # context.application.event_bus.publish('flow',
        #                                       dict(name='server.request',
        #                                       time=self.server_req_time,
        #                                       id=self.id,
        #                                       flow=self.flow))

    def update_server_resp_time(self):
        self.server_resp_time = time.time()
        # 消息总线 服务端响应请求事件，暂不使用
        # context.application.event_bus.publish('flow',
        #                                       dict(name='server.response',
        #                                       time=self.server_resp_time,
        #                                       id=self.id,
        #                                       flow=self.flow))

    def add_flow_action(self, action):
        if self.flow.get('action'):
            self.flow['action'].append(action)
        else:
            self.flow['action'] = [action]
