from lyrebird.base_server import StaticServer
from . import plugin_loader
from lyrebird import application
from flask import Blueprint, send_file
from lyrebird.log import get_logger
from types import FunctionType
import traceback

logger = get_logger()


class PluginManager(StaticServer):

    def __init__(self):
        self.plugin_path_list = []
        self.plugins = {}

    def reload(self):
        self.plugins = {}
        self.plugins.update(plugin_loader.load_all_from_ep())
        for plugin_path in self.plugin_path_list:
            try:
                plugin = plugin_loader.load_from_path(plugin_path)
            except:
                logger.error(f'Load plugin failed. Skip plugin : {plugin_path}\n{traceback.format_exc()}')
                continue
            self.plugins[plugin.project_name] = plugin
        self.setup_plugins()

    def setup_plugins(self):
        # TODO register plugins pb
        for p_name, plugin in self.plugins.items():
            view_static_folder_name = plugin.manifest.view[0]
            view_entry_file = plugin.manifest.view[1]
            plugin_static_folder = f"{plugin.location}/{view_static_folder_name}"

            # Create new blueprint for each plugin
            _bp = Blueprint(
                f'plugins_{p_name}',
                f'plugins_{p_name}',
                url_prefix=f'/plugins/{p_name}',
                static_folder=plugin_static_folder)

            # Add plugin main view to flask blueprint
            _view = plugin.manifest.view
            _index_file_path = f"{plugin.location}/{view_static_folder_name}/{view_entry_file}"
            _bp.add_url_rule('/', view_func=IndexPageViewFunc(p_name, _index_file_path))

            # Add API to blureprint
            for api in plugin.manifest.api:
                rule = api[0]
                view_func = api[1]
                if not isinstance(view_func, FunctionType):
                    logger.error(f'View func not callable. Skip API: {api}. Plugin: {p_name}')
                    continue
                if len(api) > 2:
                    methods = api[2]
                else:
                    methods = ['GET']
                _bp.add_url_rule(rule, view_func=view_func, methods=methods)

            # Register blueprint
            mock_service = application.server['mock']
            mock_service.app.register_blueprint(_bp)

            # Load background task
            for task in plugin.manifest.background:
                application.server['task'].add_task(task[0], task[1])

            # Subscribe event linstener
            event_service = application.server['event']
            for event_option in plugin.manifest.event:
                channel = event_option[0]
                callback_func = event_option[1]
                event_service.subscribe(channel, callback_func)

            # Subscribe handler on request
            for handler in plugin.manifest.on_request:
                application.on_request.append({
                    'name': handler[0],
                    'func': handler[1],
                    'rules': handler[2] if len(handler) > 2 else None
                })

            # Subscribe handler on response
            for handler in plugin.manifest.on_response:
                application.on_response.append({
                    'name': handler[0],
                    'func': handler[1],
                    'rules': handler[2] if len(handler) > 2 else None
                })

            # Subscribe handler on proxy request
            for handler in plugin.manifest.on_request_upstream:
                application.on_request_upstream.append({
                    'name': handler[0],
                    'func': handler[1],
                    'rules': handler[2] if len(handler) > 2 else None
                })

            # Subscribe handler on proxy response
            for handler in plugin.manifest.on_response_upstream:
                application.on_response_upstream.append({
                    'name': handler[0],
                    'func': handler[1],
                    'rules': handler[2] if len(handler) > 2 else None
                })

            for status_item in plugin.manifest.status:
                plugin.status.append(status_item())


class IndexPageViewFunc:

    def __init__(self, name, index_file_path):
        self.__name__ = name
        self.index_file_path = index_file_path

    def __call__(self):
        return send_file(self.index_file_path)
