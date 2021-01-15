from flask import Blueprint, request, Response

from ..handlers.mock_handler import MockHandler
from ..handlers.proxy_handler import ProxyHandler
from ..handlers.path_not_found_handler import RequestPathNotFound
from ..handlers.handler_context import HandlerContext
from ..handlers.flow_editor_handler import FlowEditorHandler
from .. import context
from lyrebird import log


logger = log.get_logger()
mock_handler = MockHandler()
proxy_handler = ProxyHandler()
path_not_found_handler = RequestPathNotFound()
flow_editor_handler = FlowEditorHandler()


core = Blueprint('mock', __name__, url_prefix='/mock')


@core.route('/', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'])
@core.route('/<path:path>', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'])
def index(path=''):
    logger.debug(f'Mock handler on request {request.url}')

    resp = None
    req_context = HandlerContext(request)
    req_context.update_client_req_time()

    flow_editor_handler.on_request_handler(req_context)

    req_context.update_server_req_time()

    mock_handler.handle(req_context)

    if not req_context.response_source:
        flow_editor_handler.on_request_upstream_handler(req_context)
        proxy_handler.handle(req_context)
        if req_context.is_proxiable:
            req_context.set_response_source_proxy()
            req_context.update_response_headers_code2flow()
            flow_editor_handler.on_response_upstream_handler(req_context)

    req_context.update_server_resp_time()

    flow_editor_handler.on_response_handler(req_context)

    if req_context.response_source:
        gen = req_context.get_response_generator()
        resp = Response(
            gen(),
            status=req_context.flow['response']['code'],
            headers=req_context.flow['response']['headers']
        )

    else:
        path_not_found_handler.handle(req_context)
        req_context.update_client_resp_time()
        resp = req_context.response

    if context.application.is_diff_mode == context.MockMode.MULTIPLE and req_context.response_source == 'mock':
        proxy_handler.handle(req_context)
        if req_context.is_proxiable:
            req_context.update_response_headers_code2flow(output_key='proxy_response')
            req_context.update_response_data2flow(output_key='proxy_response')

    context.emit('action', 'add flow log')

    return resp
