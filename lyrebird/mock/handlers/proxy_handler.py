import urllib
import requests
from requests.packages import urllib3
from flask import Response, jsonify, stream_with_context
from .. import context
from lyrebird import application
from lyrebird.log import get_logger
from lyrebird.mock import lb_http_status
from .duplicate_request_handler import DuplicateRequest
import traceback


# 关闭ssl警告
urllib3.disable_warnings()

logger = get_logger()


class ProxyHandler:
    """
    按照代理规则代理

    """

    def handle(self, handler_context, in_request_handler=True):

        request = handler_context.flow['request']

        origin_url = request.get('url')

        logger.info(f'<Proxy> {origin_url}')

        if not origin_url:
            handler_context.is_proxiable = False
            return

        parsed_url = urllib.parse.urlparse(origin_url)
        if not parsed_url.hostname:
            handler_context.is_proxiable = False
            return
        elif parsed_url.hostname in ['localhost', '127.0.0.1', ] and parsed_url.port == application.config["mock.port"]:
            DuplicateRequest().handle(handler_context)
            return

        data = handler_context.get_request_body(in_request_handler)

        method = request['method']
        headers = handler_context.get_request_headers()

        try:
            r = requests.request(
                method, 
                origin_url, 
                headers=headers, 
                data=data, 
                cookies=handler_context.get_request_cookies(in_request_handler), 
                stream=True, 
                verify=False, 
                allow_redirects=False)
            logger.info(f'<Proxy> SUCCESS {r.status_code} {origin_url}')
            
        except:
            trace_str = traceback.format_exc()
            error_response = {
                'code': 3000,
                'message': 'proxy error',
                'trace': trace_str
            } 
            resp = jsonify(error_response)
            resp.status = lb_http_status.STATUS_PROXY_ERROR
            handler_context.response = resp
            logger.info(f'<Proxy> PROXY ERROR {origin_url}\n------\ntrace:\n{trace_str}\n------\n<Proxy> PROXY ERROR {origin_url}')
            return

        # 增加数据源标记，此数据经代理得到
        resp_headers = [('lyrebird', 'proxy')]
        for name, value in r.raw.headers.items():
            # rm 'content-length' from ignore list
            if name.lower() in ('content-encoding',
                                'transfer-encoding'):
                continue
            if name.lower() == 'content-length' and 'content-encoding' in r.headers and r.headers['content-encoding'] == 'gzip':
                # 如果是gzip请求，由于requests自动解压gzip，所以此处抹去content-length,以匹配解压后的数据长度
                continue
            resp_headers.append((name, value))
        
        # HTTP Status code 204 => No content
        if r.status_code == 204:
            handler_context.response = Response(None, status=r.status_code, headers=resp_headers)
            return
        
        if in_request_handler:
            gen = stream_with_context(r.iter_content(chunk_size=handler_context.response_chunk_size))
        else:
            gen = r.iter_content(chunk_size=handler_context.response_chunk_size)

        # After huangyuanzhen test, we use 2048byte buffer :D
        handler_context.response = Response(
            gen,
            status=r.status_code,
            headers=resp_headers)
