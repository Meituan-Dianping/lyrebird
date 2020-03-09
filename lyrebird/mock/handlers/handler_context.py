from .. import context
from lyrebird import application
from lyrebird.log import get_logger
from lyrebird import utils
from urllib.parse import urlparse, unquote
import uuid
import time
import gzip
import json
import urllib
import binascii
import ipaddress
from flask import Response, stream_with_context, abort


logger = get_logger()


class HandlerContext:
    """
    请求处理器上下文变量
    用于保存一个请求处理过程中的request, response

    """
    MOCK_PATH_PREFIX = '/mock'

    STREAM = 1
    UNKNOWN = 0
    JSON = 2

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
        # self.response_state = ResponseState()
        self.response_state = None
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

        headers = {k: v for k, v in self.request.headers}
        _request = dict(
            headers=headers,
            method=self.request.method,
            query=self.request.args,
            timestamp=round(time.time(), 3)
        )
        _request.update(request_info)

        # handle request data
        if self.request.method in ['POST', 'PUT']:
            RequestDataHelper.req2dict(self.request, output=_request)

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

    def set_response_state_json(self):
        self.response_state = self.JSON

    def set_response_state_stream(self):
        if self.response_state == self.JSON:
            logger.warning('Not support changing flow response state into STREAM from JSON')
            return
        self.response_state = self.STREAM

    def set_response_state_unknown(self):
        self.response_state = self.UNKNOWN

    def update_response_info2flow(self, is_update_response_data=False):
        if not self.response:
            return

        self.flow['response'] = {
            'code': self.response.status_code,
            'headers': {k: v for (k, v) in self.response.headers},
            'timestamp': round(time.time(), 3),
            'duration': self.server_resp_time - self.client_req_time
        }

        if is_update_response_data:
            self.update_response_data2flow()

    def update_response_data2flow(self):
        ResponseDataHelper.resp2dict(self.response, output=self.flow['response'])
        if self.response.content_length:
            self.flow['size'] = self.response.content_length
        else:
            self.flow['size'] = len(self.response.data)

        if context.application.work_mode == context.Mode.RECORD:
            dm = context.application.data_manager
            dm.save_data(self.flow)

    def make_req_response(self):
        if self.response_state == self.STREAM:
            self._make_response_stream()

        if self.response_state == self.JSON:
            MockDataHelper.json2resp(self.flow['response'], output=self.flow['response'])

        if self.response_state == self.UNKNOWN:

            logger.warning(f'Data to string failed. {e}')
            return binascii.b2a_base64(data).decode('utf-8') #
            self.response = Response(
                self.flow['response'],
                status=self.flow['response']['code'],
                headers=self.flow['response']['headers']
            )

        else:
            self.response = abort(404, f'Unhandler this type of data: {self.response_state}\n')

    def _make_response_stream(self):
        def stream_copy_worker(upstream):
            try:
                buffer = []
                for item in upstream:
                    buffer.append(item)
                    yield item
            finally:
                _resp = b''
                for item in buffer:
                    _resp += item
                _resp = _resp.decode('utf-8')
                self.flow['response'] = json.dumps(_resp)
                self.update_client_resp_time()
                upstream.close()

        self.response = Response(
            stream_copy_worker(self.response.raw.stream()),
            status=self.response.status_code,
            headers=self.response.headers
            )


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
        method = self.flow['request']['method']
        url = self.flow['request']['url']
        code = self.flow['response']['code']
        duration = utils.convert_time(self.flow['duration'])
        size = utils.convert_size(self.flow['size'])
        context.application.event_bus.publish(
            'flow',
            dict(
                flow=self.flow,
                message=f"URL: {url}\nMethod: {method}\nStatusCode: {code}\nDuration: {duration}\nSize: {size}"
            )
        )

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



class DataHelper:

    @staticmethod
    def data2Str(data):
        try:
            return data.decode('utf-8')
        except Exception as e:
            logger.warning(f'Data to string failed. {e}')
            return binascii.b2a_base64(data).decode('utf-8') #


class RequestDataHelper(DataHelper):

    @staticmethod
    def req2dict(request, output=None):
        if not output:
            output = {}
        content_encoding = request.headers.get('Content-Encoding')
        # Content-Encoding handler
        unziped_data = None

        try:
            if content_encoding and content_encoding == 'gzip':
                unziped_data = gzip.decompress(request.data)

            content_type = request.headers.get('Content-Type')
            if not content_type:
                output['data'] = RequestDataHelper.data2Str(request.data)
                return

            content_type = content_type.strip()
            if content_type.startswith('application/x-www-form-urlencoded'):
                if unziped_data:
                    output['data'] = urllib.parse.parse_qs(unziped_data.decode('utf-8'))
                else:
                    output['data'] = request.form.to_dict()
            elif content_type.startswith('application/json'):
                if unziped_data:
                    output['data'] = json.loads(unziped_data.decode('utf-8'))
                else:
                    output['data'] = request.json
            elif content_type.startswith('text/xml'):
                if unziped_data:
                    output['data'] = unziped_data.decode('utf-8')
                else:
                    output['data'] = request.data.decode('utf-8')
            else:
                # TODO write bin data
                output['data'] = RequestDataHelper.data2Str(request.data)
        except Exception as e:
            output['data'] = RequestDataHelper.data2Str(request.data)
            logger.warning(f'Convert request data fail. {e}')


class ResponseDataHelper(DataHelper):

    @staticmethod
    def resp2dict(response, output=None):
        if not output:
            output = {}
        content_type = response.headers.get('Content-Type')
        if not content_type:
            output['binary_data'] = 'bin'
        else:
            content_type = content_type.strip()

        try:
            if content_type.startswith('application/json'):
                output['data'] = response.json
            elif content_type.startswith('text/xml'):
                output['data'] = response.data.decode('utf-8')
            elif content_type.startswith('text/html'):
                output['data'] = response.data.decode('utf-8')
            else:
                # TODO write bin data
                output['data'] = ResponseDataHelper.data2Str(response.data)
        except Exception as e:
            output['data'] = ResponseDataHelper.data2Str(response.data)
            logger.warning(f'Convert response failed. {e}')


class MockDataHelper(DataHelper):

    @staticmethod
    def json2resp(response, output=None):
        pass

