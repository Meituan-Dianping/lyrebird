import json
import traceback
from types import FunctionType
from flask import Blueprint, request, Response, abort

from ..handlers.mock_handler import MockHandler
from ..handlers.proxy_handler import ProxyHandler
from ..handlers.handler_context import HandlerContext, MockDataHelper
from ..handlers.flow_editor_handler import FlowEditorHandler
from .. import plugin_manager
from .. import context
from lyrebird import log
from lyrebird import application


logger = log.get_logger()
mock_handler = MockHandler()
proxy_handler = ProxyHandler()
flow_editor_handler = FlowEditorHandler()


api_mock = Blueprint('mock', __name__, url_prefix='/mock')


@api_mock.route('/', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'])
@api_mock.route('/<path:path>', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'])
def index(path=''):
    logger.debug(f'Mock handler on request {request.url}')

    resp = None
    req_context = HandlerContext(request)
    req_context.update_client_req_time()

    flow_editor_handler.on_request_handler(req_context)

    req_context.update_server_req_time()

    mock_handler.handle(req_context)

    if not req_context.flow['response']:
        flow_editor_handler.on_request_upstream_handler(req_context)
        proxy_handler.handle(req_context)
        flow_editor_handler.on_response_upstream_handler(req_context)

    req_context.update_server_resp_time()

    # old plugin loading function
    # remove later
    for plugin_name in plugin_manager.data_handler_plugins:
        try:
            plugin = plugin_manager.data_handler_plugins[plugin_name]
            plugin.handle(req_context)
            if hasattr(plugin, 'change_response'):
                if isinstance(plugin.change_response, bool) and plugin.change_response:
                    resp = req_context.response
                elif isinstance(plugin.change_response, FunctionType) and plugin.change_response():
                    resp = req_context.response
                else:
                    logger.error(f'Plugin {plugin_name} has attr change_response, but its not bool or function')
        except Exception:
            logger.error(f'plugin error {plugin_name}\n{traceback.format_exc()}')

    flow_editor_handler.on_response_handler(req_context)

    if req_context.response_state == req_context.STREAM:
        def stream_copy_worker(upstream):
            try:
                buffer = []
                for item in upstream.response:
                    buffer.append(item)
                    # TODO speedlimit
                    yield item
            finally:
                _resp = b''
                for item in buffer:
                    _resp += item
                req_context.response.data = _resp
                req_context.update_response_data2flow()
                
                req_context.update_client_resp_time()
                upstream.close()

        resp = Response(
            stream_copy_worker(req_context.response),
            status=req_context.response.status_code,
            headers=req_context.response.headers
            )

    elif req_context.response_state == req_context.JSON:
        MockDataHelper.json2resp(req_context.flow['response'], output=req_context.flow['response'])
        # length = req_context.flow['response']['headers'].get('Content-Length')

        def generator():
            try:
                size = req_context.response_chunk_size
                resp_data = req_context.flow['response']['data']
                length = len(resp_data)

                for i in range(int(length/size) + 1):
                    # TODO speedlimit
                    yield resp_data[ i * size : (i+1) * size ]
            finally:
                req_context.update_client_resp_time()

        resp = Response(
            generator(),
            status=req_context.flow['response']['code'],
            headers=req_context.flow['response']['headers']
        )

    elif req_context.response_state == req_context.INIT:
        resp = abort(404, f'Not handle this request: {req_context.flow["request"].get("url")}')
        req_context.update_client_resp_time()

    else:
        resp = abort(404, f'Unhandler this type of response data: {req_context.response_state}\n')
        req_context.update_client_resp_time()

    context.emit('action', 'add flow log')

    return resp
