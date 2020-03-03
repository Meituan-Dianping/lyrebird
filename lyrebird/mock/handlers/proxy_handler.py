import requests
from flask import Response, stream_with_context
from requests.packages import urllib3
from .. import context
import urllib
from lyrebird import application
from lyrebird.log import get_logger


# 关闭ssl警告
urllib3.disable_warnings()

logger = get_logger()


class ProxyHandler:
    """
    当前处理链上没有生成response的请求，尝试按照代理规则代理。

    """

    def handle(self, handler_context):

        request = handler_context.flow['request']

        origin_url = request.get('url')

        logger.info(f'<Proxy> {origin_url}')

        if not origin_url:
            return

        parsed_url = urllib.parse.urlparse(origin_url)
        if not parsed_url.hostname:
            return
        elif parsed_url.hostname in ['localhost', '127.0.0.1', ] and parsed_url.port == application.config["mock.port"]:
            return Response(response='Duplicate request path\n', status=400)

        method = request['method']
        data = request.get('data') or request.get('query') or None
        headers = dict()
        for name, value in request['headers'].items():
            if not value or name in ['Cache-Control', 'Host']:
                continue
            headers[name] = value

        handler_context.update_server_req_time()
        r = requests.request(method, origin_url, headers=headers, data=data, cookies=handler_context.request.cookies, 
                            stream=True, verify=False)
        handler_context.update_server_resp_time()

        # 增加数据源标记，此数据经代理得到
        resp_headers = [('lyrebird', 'proxy')]
        for name, value in r.headers.items():
            # rm 'content-length' from ignore list
            if name.lower() in ('content-encoding',
                                'transfer-encoding'):
                continue
            if name.lower() == 'content-length' and 'content-encoding' in r.headers and r.headers['content-encoding'] == 'gzip':
                # 如果是gzip请求，由于requests自动解压gzip，所以此处抹去content-length,以匹配解压后的数据长度
                continue
            resp_headers.append((name, value))

        # After huangyuanzhen test, we use 2048byte buffer :D
        return Response(
            stream_with_context(r.iter_content(chunk_size=2048)),
            status=r.status_code,
            headers=resp_headers)
