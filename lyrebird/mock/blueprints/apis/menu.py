from flask_restful import Resource
from flask import request
from lyrebird.mock import context
from lyrebird import application, reporter


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
        # When there is no actived menu, the first one is displayed by default
        if not application.active_menu:
            self.set_active_menu(menu[0])
        active_menu = application.active_menu
        active_name = active_menu.get('title', '')
        return context.make_ok_response(menu=menu, activeMenuItem=active_menu, activeName=active_name)

    def put(self):
        active_menu = request.json.get('activeMenuItem')
        self.set_active_menu(active_menu)
        return context.make_ok_response()

    def set_active_menu(self, menu):
        application.active_menu = menu
        if menu.get('params', {}).get('name'):
            menu_name = menu['params']['name']
        else:
            menu_name = menu['name']
        reporter.page_in(menu_name)
