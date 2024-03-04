from flask import Blueprint, request, Response

from ..handlers.mock_handler import MockHandler
from ..handlers.proxy_handler import ProxyHandler
from ..handlers.duplicate_header_key_handler import DuplicateHeaderKeyHandler
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


@core.route('/', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'])
@core.route('/<path:path>', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'])
def index(path=''):
    logger.info(f'<Core> On request {request.url}')

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
    elif req_context.flow['response']:
        resp = Response(
            req_context.flow['response'].get('data', ''),
            status=req_context.flow['response'].get('code', 200),
            headers=req_context.flow['response'].get('headers', {})
        )
    else:
        path_not_found_handler.handle(req_context)
        req_context.update_client_resp_time()
        resp = req_context.response

    DuplicateHeaderKeyHandler.set_origin_header(resp.headers, req_context.flow['response']['headers'])

    context.emit('action', 'add flow log')

    # Close autocorrect response location.
    resp.autocorrect_location_header = False

    return resp
