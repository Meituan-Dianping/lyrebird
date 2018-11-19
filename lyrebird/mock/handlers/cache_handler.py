import base64
import gzip
import json

from lyrebird.mock import context


class CacheHandler:
    """
    将当前request和response保存至application.cache中
    内存中保存的请求格式如下:
    {
        "request": {
            "data": null,
            "headers": {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Host": "localhost:9090",
                "User-Agent": "python-requests/2.12.4"
            },
            "method": "GET",
            "url": "http://localhost:9090/mock/http://www.baidu.com"
        },
        "response": {
            "code": 200,
            "data": "<html>...</html>",
            "headers": {
                "Cache-Control": "private, no-cache, no-store, proxy-revalidate, no-transform",
                "Content-Type": "text/html",
                "Date": "Tue, 23 May 2017 07:03:59 GMT",
                "Last-Modified": "Mon, 23 Jan 2017 13:27:31 GMT",
                "Pragma": "no-cache",
                "Server": "bfe/1.0.8.18",
                "Set-Cookie": "BDORZ=27315; max-age=86400; domain=.baidu.com; path=/"
        }
    }
    """

    def handle(self, handler_context):
        handler_context.update_client_resp_time()
        flow = self.ctx_to_dict(handler_context)
        context.application.cache.add(flow)
        context.application.socket_io.emit('action', 'add flow log')
        if context.application.work_mode == context.Mode.RECORD:
            mock_tag = flow['response']['headers']['lyrebird']
            if mock_tag.startswith('proxy'):
                group = context.application.data_manager.current_data_group
                if group:
                    group.add_data_and_filter(flow)

    def ctx_to_dict(self, handler_context):
        ctx = dict()
        ctx['id'] = handler_context.id
        ctx['time'] = handler_context.client_req_time
        ctx['response-time'] = handler_context.client_resp_time - handler_context.client_req_time
        if handler_context.request:
            req = dict()

            url = handler_context.get_origin_url()
            if url:
                req['url'] = url
            else:
                req['url'] = handler_context.request.url

            req['headers'] = {k: v for k, v in handler_context.request.headers.items()}

            # data 处理
            # 解压gzip内容
            content_type = handler_context.request.headers.get('Content-Type')
            user_agent = handler_context.request.headers.get("User-Agent")
            if 'Content-Encoding' in handler_context.request.headers \
                    and handler_context.request.headers['Content-Encoding'] == 'gzip':
                data = gzip.decompress(handler_context.request.data)
            elif handler_context.request.data[:3] == b'\x1f\x8b\x08':
                data = gzip.decompress(handler_context.request.data)
            else:
                data = handler_context.request.data
            # 保存data
            req['data'] = self.data_2_str(content_type, user_agent, data)

            req['method'] = handler_context.request.method
            ctx['request'] = req

        if handler_context.response:
            resp = dict()
            resp['code'] = handler_context.response.status_code
            resp['headers'] = {k: v for k, v in handler_context.response.headers.items()}
            content_type = handler_context.response.headers.get('Content-Type')
            user_agent = handler_context.request.headers.get("User-Agent")
            resp['data'] = self.data_2_str(content_type, user_agent, handler_context.response.data)
            ctx['response'] = resp
        return ctx

    def data_2_str(self, content_type, user_agent, data):
        if not content_type or len(data) == 0:
            return
        try:
            if 'json' in content_type:
                return json.loads(data.decode())
            elif 'text' in content_type or 'xml' in content_type:
                charset_index = content_type.find('charset')
                if charset_index >= 0:
                    charset = content_type[charset_index+8:].strip()
                    return data.decode(charset)
                else:
                    return data.decode()
            elif 'form' in content_type:
                return data.decode()
            else:
                try:
                    return json.loads(data.decode())
                except Exception:
                    return data.decode()
        except Exception:
            return 'Unknown byte data'
