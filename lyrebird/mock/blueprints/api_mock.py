import codecs
import json
import os
import traceback
from types import FunctionType
from flask import Blueprint, request, abort

from ..handlers.handler_context import HandlerContext
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

    for request_fn in application.on_request:
        handler_fn = request_fn['func']
        try:
            handler_fn(req_context)
        except Exception:
            logger.error(traceback.format_exc())

    # keep response clean
    req_context.response = None

    # old scripts loading function
    # remove later
    from lyrebird import checker
    for encoder_fn in checker.encoders:
        encoder_fn(req_context)

    for handler_name in plugin_manager.inner_handler:
        handler = plugin_manager.inner_handler[handler_name]
        try:
            handler.handle(req_context)
            if req_context.response:
                resp = req_context.response
        except Exception:
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

    if not resp:
        resp = abort(404, 'Not handle this request')

    for response_fn in application.on_response:
        handler_fn = response_fn['func']
        try:
            handler_fn(req_context)
        except Exception:
            logger.error(traceback.format_exc())

    req_context.update_client_resp_time()

    context.emit('action', 'add flow log')

    return resp
