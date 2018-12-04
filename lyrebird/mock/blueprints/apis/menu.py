from flask_restful import Resource
from flask import jsonify
from lyrebird.mock import context
from lyrebird.mock import plugin_manager


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
            }]
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
                    'src': f'/ui/plugin/{plugin["project_name"]}',
                    'name': name
                }
            })
        return context.make_ok_response(menu=menu)
