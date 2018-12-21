from .. import context
from lyrebird import application
from urllib.parse import urlparse
import uuid
import time


class HandlerContext:
    """
    请求处理器上下文变量
    用于保存一个请求处理过程中的request, response

    """
    MOCK_PATH_PREFIX = '/mock'

    def __init__(self, request, raw_path):
        self.id = str(uuid.uuid4())
        self.request = request
        self._raw_path = raw_path
        self._response = None
        self.client_req_time = None
        self.client_resp_time = None
        self.server_req_time = None
        self.server_resp_time = None
        self.flow = dict(id=self.id, size=0, duration=0)
        self.client_address = None
        self._parse_request()

    
    def _parse_request(self):
        # Read stream
        self.request.get_data()
        # parse path
        request_info = self._read_origin_request_info_from_url()
        if not request_info['host']:
            request_info = self._read_origin_request_info_from_header()

        headers = {k:v for k,v in self.request.headers}
        _request = dict(
            headers=headers,
            method=self.request.method,
            )
        _request.update(request_info)
        
        # handle request data
        if self.request.method in ['POST', 'PUT']:
            RequestDataHelper.req2dict(self.request, output=_request)
        
        if self.request.headers.get('Lyrebird-Client-Address'):
            self.client_address = self.request.headers.get('Lyrebird-Client-Address')
        else:
            self.client_address = self.request.remote_addr
    
        self.flow['request'] = _request
        context.application.cache.add(self.flow)

    def _read_origin_request_info_from_url(self):
        path_index = self.request.url.index(self._raw_path)
        url = self.request.url[path_index:]
        parsed_path = urlparse(url)
        _request = dict(
            url=url,
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
        return dict(
            url=scheme+'://'+host+':'+port+self.request.full_path[len(self.MOCK_PATH_PREFIX):],
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
            headers={k:v for (k,v) in self._response.headers}
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
        # 消息总线 客户端请求事件
        context.application.event_bus.publish('flow',
                                              dict(name='client.request',
                                              time=self.client_req_time,
                                              id=self.id,
                                              flow=self.flow
                                              ))

    def update_client_resp_time(self):
        self.client_resp_time = time.time()
        # 消息总线 客户端响应事件
        context.application.event_bus.publish('flow',
                                              dict(name='client.response',
                                              time=self.client_resp_time,
                                              id=self.id,
                                              flow=self.flow))

    def update_server_req_time(self):
        self.server_req_time = time.time()
        # 消息总线 客户端请求事件
        context.application.event_bus.publish('flow',
                                              dict(name='server.request',
                                              time=self.server_req_time,
                                              id=self.id,
                                              flow=self.flow))

    def update_server_resp_time(self):
        self.server_resp_time = time.time()
        # 消息总线 客户端请求事件
        context.application.event_bus.publish('flow',
                                              dict(name='server.response',
                                              time=self.server_resp_time,
                                              id=self.id,
                                              flow=self.flow))

    def get_origin_url(self):
        return self.flow['request']['url']


class RequestDataHelper:

    @staticmethod
    def req2dict(request, output=None):
        if not output:
            output = {}
        content_type = request.headers.get('Content-Type')
        if not content_type:
            output['binary_data'] =  'bin'
        else:
            content_type = content_type.strip()

        if content_type.startswith('application/x-www-form-urlencoded'):
            output['data'] = request.form.to_dict()
        elif content_type.startswith('application/json'):
            output['data'] = request.json
        elif content_type.startswith('text/xml'):
            output['data'] = request.data.decode('utf-8')
        else:
            # TODO write bin data
            output['binary_data'] =  'bin'


class ResponseDataHelper:

    @staticmethod
    def resp2dict(response, output=None):
        if not output:
            output = {}
        content_type = response.headers.get('Content-Type')
        if not content_type:
            output['binary_data'] = 'bin'
        else:
            content_type = content_type.strip()
        
        if content_type.startswith('application/json'):
            output['data'] = response.json
        elif content_type.startswith('text/xml'):
            output['data'] = response.data.decode('utf-8')
        elif content_type.startswith('text/html'):
            output['data'] = response.data.decode('utf-8')
        else:
            # TODO write bin data
            output['binary_data'] =  'bin'
