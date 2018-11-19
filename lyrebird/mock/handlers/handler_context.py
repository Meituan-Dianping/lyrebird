from flask import Request, Response
from .. import context
from lyrebird import application
import uuid
import time


class HandlerContext:
    """
    请求处理器上下文变量
    用于保存一个请求处理过程中的request, response

    """

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.request: Request = None
        self.response: Response = None
        self.client_req_time = None
        self.client_resp_time = None
        self.server_req_time = None
        self.server_resp_time = None
        self.flow = {'id': self.id}
        self.client_address = None

    def get_client_address(self):
        """
        用于识别设备ip的函数
        启动传参的request，通过remote_addr获取deviceip
        经由proxy的request，header已加deviceip，通过headers获取deviceip
        """
        if self.request.headers.get('Lyrebird-Client-Address'):
            self.client_address = self.request.headers.get('Lyrebird-Client-Address')
        else:
            self.client_address = self.request.remote_addr
    

    def update_client_req_time(self):
        self.client_req_time = time.time()
        self.request2dict()
        # 消息总线 客户端请求事件
        context.application.event_bus.publish('flow',
                                              dict(name='client.request',
                                                   time=self.client_req_time,
                                                   id=self.id,
                                                   flow=self.flow
                                                   ))

    def update_client_resp_time(self):
        self.client_resp_time = time.time()
        self.response2dict()
        # 消息总线 客户端响应事件
        context.application.event_bus.publish('flow',
                                              dict(name='client.response',
                                                   time=self.client_resp_time,
                                                   id=self.id,
                                                   flow=self.flow))

    def update_server_req_time(self):
        self.server_req_time = time.time()
        self.request2dict()
        # 消息总线 客户端请求事件
        context.application.event_bus.publish('flow',
                                              dict(name='server.request',
                                                   time=self.server_req_time,
                                                   id=self.id,
                                                   flow=self.flow))

    def update_server_resp_time(self):
        self.server_resp_time = time.time()
        self.response2dict()
        # 消息总线 客户端请求事件
        context.application.event_bus.publish('flow',
                                              dict(name='server.response',
                                                   time=self.server_resp_time,
                                                   id=self.id,
                                                   flow=self.flow))

    def get_origin_url(self):
        proxy_headers = application.config['mock.proxy_headers']
        scheme = self.request.headers.get(proxy_headers['scheme'], default='http')
        host = self.request.headers.get(proxy_headers['host'])
        port = self.request.headers.get(proxy_headers['port'], default='80')
        url_index = self.request.url.find('/mock/')
        if scheme and host and port:
            scheme = scheme.strip()
            host = host.strip()
            port = port.strip()
            if port == '80':
                url = scheme+'://'+host
            else:
                url = scheme+'://'+host+':'+port
            if self.request.path and len(self.request.path[len('/mock'):]) > 0:
                url = url + self.request.path[len('/mock'):]
            query_string = self.request.query_string.decode()
            if query_string:
                url = url + '?' + query_string
            return url
        elif url_index > 0:
            return self.request.url[url_index + 6:]
        else:
            return None

    def request2dict(self):
        if self.request is None:
            return
        req = {}
        req['url'] = self.request.url
        req['method'] = self.request.method
        req['headers'] = [{'name':header[0], 'value':header[1]} for header in self.request.headers]
        self.flow['request'] = req

    def response2dict(self):
        if self.response is None:
            return
        resp = {}
        resp['status'] = self.response.status_code
        resp['headers'] = [{'name': header[0], 'value': header[1]} for header in self.response.headers]
        self.flow['response'] = resp
