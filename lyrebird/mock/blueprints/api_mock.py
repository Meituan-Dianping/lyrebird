import traceback
from types import FunctionType
from flask import Blueprint, request, Response, abort

from ..handlers.mock_handler import MockHandler
from ..handlers.proxy_handler import ProxyHandler
from ..handlers.handler_context import HandlerContext
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

    # TODO change api_mock.py into core.py

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

    if req_context.response_state == req_context.STRING:
        req_context.transfer_response_state_string()

    if req_context.response_state == req_context.STREAM:
        gen = req_context.get_response_gen_stream()

    elif req_context.response_state == req_context.JSON:
        gen = req_context.get_response_gen_json()

    elif req_context.response_state == req_context.BYTES:
        gen = req_context.get_response_gen_bytes()

    elif req_context.response_state == req_context.UNKNOWN:
        gen = req_context.get_response_gen_unknown()

    else:
        resp = abort(404, f'Not handle this request: {req_context.flow["request"].get("url")}')
        req_context.update_client_resp_time()

    resp = Response(
        gen(),
        status=req_context.flow['response']['code'],
        headers=req_context.flow['response']['headers']
    )

    context.emit('action', 'add flow log')

    return resp
