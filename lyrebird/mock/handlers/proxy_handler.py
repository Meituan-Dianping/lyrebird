import requests
from flask import Response, stream_with_context
from requests.packages import urllib3
from .. import context
import urllib
from lyrebird import application


# 关闭ssl警告
urllib3.disable_warnings()


class ProxyHandler:
    """
    当前处理链上没有生成response的请求，尝试按照代理规则代理。

    """
    def handle(self, handler_context):
        if handler_context.response:
            handler_context.response.headers.add_header("isMocked", "True")
            return
        request = handler_context.request

        origin_url = handler_context.get_origin_url()

        if not origin_url:
            return

        parsed_url = urllib.parse.urlparse(origin_url)
        if not parsed_url.hostname:
            return
        elif parsed_url.hostname in ['localhost', '127.0.0.1', ] and parsed_url.port == application.config["mock.port"]:
            handler_context.response = Response(response='Duplicate request path\n', status=400)
            return
        
        method = request.method
        data = request.get_data() or request.form or None
        headers = dict()
        for name, value in request.headers:
            if not value or name in ['Cache-Control', 'Host']:
                continue
            headers[name] = value

        handler_context.update_server_req_time()
        r = requests.request(method, origin_url, headers=headers, data=data, cookies=request.cookies, stream=True,
                             verify=False)

        # 增加数据源标记，此数据经代理得到
        resp_headers = [('lyrebird', 'proxy')]
        for name, value in r.headers.items():
            # rm 'content-length' from ignore list
            if name.lower() in ('content-encoding',
                                'transfer-encoding'):
                continue
            if name.lower() == 'content-length' and 'content-encoding' in r.headers and r.headers['content-encoding']=='gzip':
                # 如果是gzip请求，由于requests自动解压gzip，所以此处抹去content-length,以匹配解压后的数据长度
                continue
            resp_headers.append((name, value))
        
        handler_context.request.url = origin_url
        
        # After huangyuanzhen test, we use 2048byte buffer :D
        handler_context.response = Response(
            stream_with_context(r.iter_content(chunk_size=2048)),
            status=r.status_code,
            headers=resp_headers)
