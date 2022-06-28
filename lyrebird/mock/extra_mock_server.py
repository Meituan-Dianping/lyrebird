import asyncio
import re
import traceback
from aiohttp import web, client
from urllib import parse as urlparse

import sys
import json
import multiprocessing
from typing import List, Set, Optional

from lyrebird import application
from lyrebird.log import get_logger

logger = get_logger()

lb_config = {}


class UnknownLyrebirdProxyProtocol(Exception):
    pass


class GracefulExit(SystemExit):
    code = 1


class LyrebirdProxyContext:
    def __init__(self):
        self.request: web.Request = None
        self.netloc = None
        self.origin_url = None
        self.forward_url = None

    @classmethod
    def parse(cls, request: web.Request,
              lb_proxy_scheme_header_name='LBOriginScheme',
              lb_proxy_host_header_name='LBOriginHost',
              lb_proxy_port_header_name='LBOriginPort',
              lb_proxy_query_keys: Optional[List] = None):

        global lb_config

        # Lyrebird proxy protocol #1
        # Origin target info in path
        # e.g.
        # http://{lyrebird_host}/{origin_full_url}
        if request.path.startswith('/http://') or request.path.startswith('/https://'):
            origin_full_url = request.path_qs[1:]
            url = urlparse.urlparse(origin_full_url)

            ctx = cls()
            # origin url for proxy
            ctx.origin_url = origin_full_url
            # forward url to lyrebird main port 'default 9090'
            port = lb_config.get('mock.port')
            ctx.forward_url = f'http://127.0.0.1:{port}/mock/{origin_full_url}'

            ctx.netloc = url.netloc
            ctx.request = request
            return ctx

        # Lyrebird proxy protocol #2
        # Origin target info in headers
        # e.g.
        # http://{lyrebird_host}/{origing_path_and_query}
        # headers:
        # MKScheme: {origin_scheme}
        # MKOriginHost: {origin_host}
        # MKOriginPort: {origin_port}
        if request.headers.get(lb_proxy_host_header_name) and request.headers.get(lb_proxy_scheme_header_name):
            target_scheme = request.headers.get(lb_proxy_scheme_header_name)
            target_host = request.headers.get(lb_proxy_host_header_name)
            target_port = request.headers.get(lb_proxy_port_header_name)
            if target_port:
                origin_full_url = f'{target_scheme}://{target_host}:{target_port}{request.rel_url}'
                netloc = f'{target_host}:{target_port}'
            else:
                origin_full_url = f'{target_scheme}://{target_host}{request.rel_url}'
                netloc = target_host

            ctx = cls()
            # origin url for proxy
            ctx.origin_url = origin_full_url
            # forward url to lyrebird main port 'default 9090'
            port = lb_config.get('mock.port')
            ctx.forward_url = f'http://127.0.0.1:{port}/mock/{origin_full_url}'
            ctx.netloc = netloc
            ctx.request = request
            return ctx

        # Lyrebird proxy protocol #3
        # Origin target info in query
        # default key is "proxy" or "mp_webview_domain_info"
        # e.g.
        # http://{lyrebird_host}/{origing_path}?{proxy=encoded-url or custom_query_key=encoded-url}

        # set default key=proxy
        if lb_proxy_query_keys is None:
            lb_proxy_query_keys = ['proxy']
        elif 'proxy' not in lb_proxy_query_keys:
            lb_proxy_query_keys.append('proxy')

        def contain_custom_query_key(request: web.Request, lb_proxy_query_keys):
            for query_key in lb_proxy_query_keys:
                if request.query.get(query_key):
                    return True, query_key
            return False, query_key

        has_custom_key, query_key = contain_custom_query_key(request, lb_proxy_query_keys)
        if has_custom_key:
            origin_url = request.query.get(query_key)
            origin_url = urlparse.unquote(origin_url)
            url = urlparse.urlparse(origin_url)

            ctx = cls()
            ctx.origin_url = origin_url
            # forward url to lyrebird main port 'default 9090'
            port = lb_config.get('mock.port')
            ctx.forward_url = f'http://127.0.0.1:{port}/mock/?{query_key}={urlparse.quote(origin_url)}'
            ctx.netloc = url.netloc
            ctx.request = request
            return ctx

        raise UnknownLyrebirdProxyProtocol


def is_filtered(context: LyrebirdProxyContext):
    '''
    Copy from lyrebird proxy

    allow list like
    '''
    global lb_config
    filters = lb_config.get('proxy.filters')
    for _filter in filters:
        if re.search(_filter, context.origin_url):
            return True
    return False


def make_raw_headers_line(request: web.Request):
    raw_headers = {}
    for k, v in request.raw_headers:
        raw_header_name = k.decode()
        raw_header_value = v.decode()
        if raw_header_name.lower() in ['cache-control', 'host', 'transfer-encoding']:
            continue
        raw_headers[raw_header_name] = raw_header_value
    return json.dumps(raw_headers, ensure_ascii=False)


async def send_request(context: LyrebirdProxyContext, target_url):
    async with client.ClientSession(auto_decompress=False) as session:
        request: web.Request = context.request
        headers = {k: v for k, v in request.headers.items() if k.lower() not in [
            'cache-control', 'host', 'transfer-encoding']}
        headers['Proxy-Raw-Headers'] = make_raw_headers_line(request)
        request_body = None
        if request.body_exists:
            request_body = request.content
        async with session.request(request.method,
                                   target_url,
                                   headers=headers,
                                   data=request_body,
                                   verify_ssl=False,
                                   allow_redirects=False,
                                   raise_for_status=False) as _resp:
            proxy_resp_status = _resp.status
            proxy_resp_headers = _resp.headers
            # TODO support stream response
            proxy_resp_data = await _resp.read()

    response_headers = {}
    for k, v in proxy_resp_headers.items():
        if k.lower() in ['transfer-encoding']:
            continue
        elif k.lower() == 'content-length':
            response_headers[k] = str(len(proxy_resp_data))
        elif k.lower() == 'host':
            response_headers['Host'] = context.netloc
        elif k.lower() == 'location':
            response_headers['Host'] = context.netloc
            response_headers[k] = v
        else:
            response_headers[k] = v

    resp = web.Response(status=proxy_resp_status, body=proxy_resp_data, headers=response_headers)
    return resp


async def proxy(context: LyrebirdProxyContext):
    logger.info(f'proxy {context.origin_url}')
    return await send_request(context, context.origin_url)


async def forward(context: LyrebirdProxyContext):
    logger.info(f'forward {context.forward_url}')
    return await send_request(context, context.forward_url)


async def req_handler(request: web.Request):
    try:
        global lb_config
        header_name_scheme = lb_config.get('mock.proxy_headers', {}).get('scheme')
        header_name_host = lb_config.get('mock.proxy_headers', {}).get('host')
        header_name_port = lb_config.get('mock.proxy_headers', {}).get('port')
        query_keys = lb_config.get('mock.proxy_query_keys')
        proxy_ctx = LyrebirdProxyContext.parse(request,
                                               lb_proxy_scheme_header_name=header_name_scheme,
                                               lb_proxy_host_header_name=header_name_host,
                                               lb_proxy_port_header_name=header_name_port,
                                               lb_proxy_query_keys=query_keys)
        if is_filtered(proxy_ctx):
            # forward to lyrebird
            return await forward(proxy_ctx)
        else:
            # proxy
            return await proxy(proxy_ctx)
    except Exception as e:
        logger.error(f'[Exception] Extra mock server:\n{request.url}\n{traceback.format_exc()}')
        return web.Response(status=500, text=f'{e.__class__.__name__}')


async def _run_app(config):
    global lb_config
    lb_config = config

    port = config.get('extra.mock.port')
    port = port if port else 9999

    app = web.Application()
    app.router.add_route('*', r'/{path:(.*)}', req_handler)

    try:
        app_runner = web.AppRunner(app, auto_decompress=False)
        await app_runner.setup()

        web_site = web.TCPSite(app_runner, '0.0.0.0', port)
        await web_site.start()

        if print:
            names = sorted(str(s.name) for s in app_runner.sites)
            print(
                "======== Running on {} ========\n"
                "(Press CTRL+C to quit)".format(", ".join(names))
            )

        # sleep forever by 1 hour intervals,
        # on Windows before Python 3.8 wake up every 1 second to handle
        # Ctrl+C smoothly
        if sys.platform == "win32" and sys.version_info < (3, 8):
            delay = 1
        else:
            delay = 3600

        while True:
            await asyncio.sleep(delay)
    finally:
        await app_runner.cleanup()


def _cancel_tasks(
    to_cancel: Set["asyncio.Task[Any]"], loop: asyncio.AbstractEventLoop
) -> None:
    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(asyncio.gather(*to_cancel, return_exceptions=True))

    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "unhandled exception during asyncio.run() shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )


def serve(config):
    loop = asyncio.new_event_loop()
    main_task = loop.create_task(_run_app(config))

    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main_task)
    except (GracefulExit, KeyboardInterrupt):
        pass
    finally:
        _cancel_tasks({main_task}, loop)
        _cancel_tasks(asyncio.all_tasks(loop), loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


class ExtraMockServer():
    def __init__(self) -> None:
        self._server_process = None

    def start(self):
        self._server_process = multiprocessing.Process(
            group=None,
            daemon=True,
            target=serve,
            kwargs={'config': application.config.raw()})
        self._server_process.start()

    def stop(self):
        if self._server_process:
            self._server_process.terminate()
            logger.warning(f'MockServer shutdown')
            self._server_process = None
