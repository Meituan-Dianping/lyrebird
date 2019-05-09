from .. import context
from lyrebird import application
from lyrebird.log import get_logger
from urllib.parse import urlparse
import urllib
import uuid
import time
import gzip
import json
import ipaddress
import binascii


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
        self._response = None
        self.client_req_time = None
        self.client_resp_time = None
        self.server_req_time = None
        self.server_resp_time = None
        self.flow = dict(
            id=self.id,
            size=0,
            duration=0,
            start_time=time.time())
        self.client_address = None
        self._parse_request()


    def _parse_request(self):
        # Read stream
        self.request.get_data()
        # parse path
        request_info = self._read_origin_request_info_from_url()
        if not request_info['host']:
            request_info_from_header = self._read_origin_request_info_from_header()
            if len(request_info_from_header)>0 :
                request_info = request_info_from_header

        headers = {k:v for k,v in self.request.headers}
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
        url_prefix = self.request.url_root+self.request.blueprint+'/'
        raw_url = self.request.url[len(url_prefix):]
        parsed_path = urlparse(raw_url)
        _request = dict(
            url=raw_url,
            scheme=parsed_path.scheme,
            host=parsed_path.hostname,
            port=parsed_path.port if parsed_path.port else '80',
            path=parsed_path.path
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

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, val):
        self._response = val
        self.update_server_resp_time()

        _response = dict(
            code=self._response.status_code,
            headers={k:v for (k,v) in self._response.headers},
            timestamp=round(time.time(), 3)
        )

        ResponseDataHelper.resp2dict(self._response, output=_response)
        self.flow['response'] = _response

        if val.content_length:
            self.flow['size'] = val.content_length
        else:
            self.flow['size'] = len(val.data)
        self.flow['duration'] = self.server_resp_time - self.client_req_time

        if context.application.work_mode == context.Mode.RECORD:
            dm = context.application.data_manager
            group = dm.groups.get(dm.activated_group_id)
            if group:
                data = group.create_data(flow=self.flow)
                data.save()

    def _read_response_info(self):
        self._response.headers.get('Content-Type')

    def update_client_req_time(self):
        self.client_req_time = time.time()
        # 消息总线 客户端请求事件，暂不使用
        # context.application.event_bus.publish('flow',
        #                                       dict(name='client.request',
        #                                       time=self.client_req_time,
        #                                       id=self.id,
        #                                       flow=self.flow
        #                                       ))

    def update_client_resp_time(self):
        self.client_resp_time = time.time()
        # 消息总线 客户端响应事件， 目前仅启用此事件
        context.application.event_bus.publish('flow',
        dict(
            flow=self.flow,
            message=f"URL:{self.flow['request']['url']}\nStatusCode:{self.flow['response']['code']}\nDuration:{self.flow['duration']}\nSize:{self.flow['size']}"
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

    def get_origin_url(self):
        return self.flow['request'].get('url')


class DataHelper:

    @staticmethod
    def data2Str(data):
        try:
            return data.decode('utf-8')
        except Exception as e:
            logger.warning(f'Data to string failed. {e}')
            return binascii.b2a_base64(data).decode('utf-8')


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
                output['data'] =  RequestDataHelper.data2Str(request.data)
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
                output['data'] =  RequestDataHelper.data2Str(request.data)
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
                output['data'] =  ResponseDataHelper.data2Str(response.data)
        except Exception as e:
            output['data'] = ResponseDataHelper.data2Str(response.data)
            logger.warning(f'Convert response failed. {e}')

