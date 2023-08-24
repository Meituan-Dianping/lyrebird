
import asyncio
import re
import traceback
from aiohttp import web, client
from yarl import URL

import sys
import json
from typing import List, Set, Optional

from lyrebird.mock.extra_mock_server.lyrebird_proxy_protocol import LyrebirdProxyContext
from lyrebird import log

logger = None
lb_config = {}


def is_filtered(context: LyrebirdProxyContext):
    '''
    Copy from lyrebird proxy

    allow list like
    '''
    global lb_config
    filters = lb_config.get('proxy.filters', [])
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
        async with session.request(
            request.method,
            URL(target_url, encoded=True),
            headers=headers,
            data=request_body,
            verify_ssl=False,
            allow_redirects=False,
            raise_for_status=False
        ) as _resp:
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
    try:
        return await send_request(context, context.forward_url)
    except Exception:
        logger.debug(f'Forward request error, it may caused by mock server not ready. URL: {context.forward_url}')


async def req_handler(request: web.Request):
    try:
        global lb_config
        proxy_ctx = LyrebirdProxyContext.parse(request, lb_config)
        if is_filtered(proxy_ctx):
            # forward to lyrebird
            return await forward(proxy_ctx)
        else:
            # proxy
            return await proxy(proxy_ctx)
    except Exception as e:
        logger.error(f'[Exception] Extra mock server:\n{request.url}\n{traceback.format_exc()}')
        return web.Response(status=500, text=f'{e.__class__.__name__}')


def init_app(config):
    global lb_config
    lb_config = config

    global logger
    log.init(config)
    logger = log.get_logger()

    app = web.Application()
    app.router.add_route('*', r'/{path:(.*)}', req_handler)

    return app


async def _run_app(config):
    app = init_app(config)

    port = config.get('extra.mock.port')
    port = port if port else 9999

    try:
        app_runner = web.AppRunner(app, auto_decompress=False)
        await app_runner.setup()

        web_site = web.TCPSite(app_runner, '0.0.0.0', port)
        await web_site.start()

        # app sites list, not display in log.
        # names = sorted(str(s.name) for s in app_runner.sites)
        logger.log(60, f'Extra mock server start on {port}')

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

def publish_init_status(queue, status):
    queue.put({
        'type': 'event',
        "channel": "system",
        "content": {
            'system': {
                'action': 'init_module',
                'status': status,
                'module': 'extra_mock'
            }
        }
    })


def serve(queue, config, *args, **kwargs):
    loop = asyncio.new_event_loop()
    main_task = loop.create_task(_run_app(config))

    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main_task)
    except KeyboardInterrupt:
        publish_init_status(queue, 'ERROR')
    finally:
        _cancel_tasks({main_task}, loop)
        _cancel_tasks(asyncio.all_tasks(loop), loop)
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
