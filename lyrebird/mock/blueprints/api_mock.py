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


logger = log.get_logger()


api_mock = Blueprint('mock', __name__, url_prefix='/mock')


@api_mock.route('/', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'])
@api_mock.route('/<path:path>', methods=['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'])
def index(path=''):
    logger.debug(f'Mock handler on request {request.url}')

    resp = None
    req_context = HandlerContext(request)
    req_context.update_client_req_time()

    for handler_name in plugin_manager.inner_handler:
        handler = plugin_manager.inner_handler[handler_name]
        logger.debug(f'Call inner handler {handler_name}')
        try:
            handler.handle(req_context)
            if req_context.response:
                resp = req_context.response
        except Exception:
            logger.error(traceback.format_exc())

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

    req_context.update_client_resp_time()

    context.emit('action', 'add flow log')

    return resp
