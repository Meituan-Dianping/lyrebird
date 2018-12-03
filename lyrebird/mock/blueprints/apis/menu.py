from flask_restful import Resource
from flask import jsonify
from lyrebird.mock import context
from lyrebird.mock import plugin_manager


class Menu(Resource):

    def get(self):
        menu = [
            {
                'name': 'Inspector',
                'type': 'router',
                'path': '/'
            },
            {
                'name': 'DataManager',
                'type': 'router',
                'path': '/datamanager'
            }]
        for plugin_key in plugin_manager.plugins:
            plugin = plugin_manager.plugins[plugin_key]
            if 'beta_web' not in plugin:
                continue
            web = plugin['beta_web']
            name = plugin['name']
            if hasattr(web, 'get_title'):
                name = web.get_title()
            menu.append({
                'name': name,
                'type': 'router',
                'path': '/plugin',
                'params': {
                    'src': f'/plugin/{plugin["name"]}'
                }
            })
        # append mock menu
        menu.append({
                'name': 'PluginX',
                'type': 'router',
                'path': '/plugin',
                'params': {
                    'src': '/plugin/demo'
                }
            })
        return context.make_ok_response(menu=menu)
