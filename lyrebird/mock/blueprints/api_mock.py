import re
import traceback
from types import FunctionType
from flask import Blueprint, request, Response, stream_with_context

from ..handlers.mock_handler import MockHandler
from ..handlers.proxy_handler import ProxyHandler
from ..handlers.handler_context import HandlerContext
from ..handlers.path_not_found_handler import RequestPathNotFound
from .. import plugin_manager
from .. import context
from lyrebird import log
from lyrebird import application


logger = log.get_logger()


api_mock = Blueprint('mock', __name__, url_prefix='/mock')


@api_mock.route('/', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'])
@api_mock.route('/<path:path>', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'])
def index(path=''):
    logger.debug(f'Mock handler on request {request.url}')

    resp = None
    req_context = HandlerContext(request)
    req_context.update_client_req_time()

    # on_request
    for request_fn in application.on_request:
        if request_fn['rules'] and not _is_req_match_rule(request_fn['rules'], req_context.flow):
            continue
        handler_fn = request_fn['func']
        try:
            handler_fn(req_context.flow['request'])
        except Exception:
            logger.error(traceback.format_exc())

    # old scripts loading function
    # remove later
    from lyrebird import checker
    for encoder_fn in checker.encoders:
        encoder_fn(req_context)

    # mock handler
    try:
        mock_res = MockHandler().handle(req_context)
    except Exception:
        mock_res = None
        logger.error(traceback.format_exc())
    if mock_res:
        req_context.flow['response'] = mock_res['response']
        req_context.flow['response']['headers']['isMocked'] = 'True'
        req_context.flow['response']['headers']['lyrebird'] = 'mock'

    # proxy
    else:
        # on_request_upstream
        for request_fn in application.on_request_upstream:
            if request_fn['rules'] and not _is_req_match_rule(request_fn['rules'], req_context.flow):
                continue
            handler_fn = request_fn['func']
            try:
                handler_fn(req_context.flow['request'])
            except Exception:
                req_context._parse_request()
                logger.error(traceback.format_exc())

        # proxy handler
        req_context.update_server_req_time()
        try:
            req_context.response = ProxyHandler().handle(req_context)
        except Exception:
            logger.error(traceback.format_exc())
        req_context.update_server_resp_time()

        # on_response_upstream
        _matched_on_response_upstream = []
        req_context.update_response_into_flow()
        for response_fn in application.on_response_upstream:
            if response_fn['rules'] and not _is_req_match_rule(response_fn['rules'], req_context.flow):
                continue
            _matched_on_response_upstream.append(response_fn)
        if not _matched_on_response_upstream:
            req_context.flow['response'] = {}
        else:
            req_context.update_response_into_flow(is_update_response_data=True)
            for response_fn in _matched_on_response_upstream:
                handler_fn = response_fn['func']
                try:
                    handler_fn(req_context.flow['response'])
                except Exception:
                    req_context.update_response_into_flow(is_update_response_data=True)
                    logger.error(traceback.format_exc())

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

    # on_response
    if not req_context.flow.get('response') and req_context.response:
        req_context.update_response_into_flow()
        for response_fn in application.on_response:
            if response_fn['rules'] and not _is_req_match_rule(response_fn['rules'], req_context.flow):
                continue
            req_context.update_response_into_flow(is_update_response_data=True)
            break
    for response_fn in application.on_response:
        if response_fn['rules'] and not _is_req_match_rule(response_fn['rules'], req_context.flow):
            continue
        handler_fn = response_fn['func']
        try:
            handler_fn(req_context.flow['response'])
        except Exception:
            logger.error(traceback.format_exc())

    if req_context.flow.get('response'):
        def gen():
            yield req_context.flow['response']['data']
        req_context.update_client_resp_time()
        resp = Response(
            stream_with_context(gen()),
            status=req_context.flow['response']['code'],
            headers=req_context.flow['response']['headers']
        )

    elif req_context.response:
        def gen():
            buffer = b''
            while True:
                yield req_context.response.data
                buffer += req_context.response.data
                if len(buffer) >= len(req_context.response.data):
                    break
            req_context.update_response_into_flow(is_update_response_data=True, response_data=buffer.decode('utf-8'))
            req_context.update_client_resp_time()
        resp = Response(
            stream_with_context(gen()),
            status=req_context.response.status_code,
            headers=req_context.response.headers
        )

    else:
        resp = RequestPathNotFound().handle(req_context)
        req_context.update_client_resp_time()

    context.emit('action', 'add flow log')

    return resp

def _is_req_match_rule(rules, flow):
    if not rules:
        return False
    for rule_key in rules:
        pattern = rules[rule_key]
        target = _get_rule_target(rule_key, flow)
        if not target or not re.search(pattern, target):
            return False
    return True

def _get_rule_target(rule_key, flow):
    prop_keys = rule_key.split('.')
    result = flow
    for prop_key in prop_keys:
        result = result.get(prop_key)
        if not result:
            return None
    return result
