from flask_restful import Resource
from flask import jsonify,request
from lyrebird.mock import context
from lyrebird.mock import plugin_manager
from lyrebird import application


class Menu(Resource):

    def get(self):
        menu = [
            {
                'name': 'inspector',
                'title': 'Inspector',
                'type': 'router',
                'path': '/'
            },
            {
                'name': 'datamanager',
                'title': 'DataManager',
                'type': 'router',
                'path': '/datamanager'
            },
            {
                'name': 'checker',
                'title': 'Checker',
                'type': 'router',
                'path': '/checker'
            }]
        # Load plugins from new plugin manager
        _pm = application.server['plugin']
        for plugin_id, plugin in _pm.plugins.items():
            menu.append({
                'name': 'plugin-container',
                'title': plugin.manifest.name,
                'type': 'router',
                'path': '/plugins',
                'params': {
                    'src': f'/plugins/{plugin_id}',
                    'name': plugin_id
                }
            })
        # Load old plugins
        # TODO remove after all plugin use new manifest function
        for plugin_key in plugin_manager.plugins:
            plugin = plugin_manager.plugins[plugin_key]
            if 'beta_web' not in plugin:
                continue
            web = plugin['beta_web']
            name = plugin['name']
            if hasattr(web, 'get_title'):
                title = web.get_title()
            else:
                title = name[0].upper() + name[1:]
            menu.append({
                'name': 'plugin-view',
                'title': title,
                'type': 'router',
                'path': '/plugin',
                'params': {
                    'src': f'/plugin/{plugin["project_name"]}',
                    'name': name
                }
            })
        # When there is no actived menu, the first one is displayed by default
        active_menu = application.active_menu or menu[0]
        active_name = active_menu.get('title', '')
        return context.make_ok_response(menu=menu, activeMenuItem=active_menu, activeName=active_name)

    def put(self):
        active_menu = request.json.get('activeMenuItem')
        application.active_menu = active_menu
        return context.make_ok_response()
