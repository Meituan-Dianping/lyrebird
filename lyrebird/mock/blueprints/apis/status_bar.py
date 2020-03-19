from flask_restful import Resource
from lyrebird import application


class StatusBar(Resource):

    def get(self, item_id=None):
        if item_id == None:
            return self._get_all_status_item()
        else:
            return self._get_menu_by_status_item_id(item_id)

    def _get_all_status_item(self):
        all_status_item = []
        plugin_server = application.server['plugin']
        for plugin_name in plugin_server.plugins:
            plugin = plugin_server.plugins[plugin_name]
            for status_item in plugin.status:
                all_status_item.append({'id': status_item.id, 'text': status_item.get_text()})
        return application.make_ok_response(data=all_status_item)

    def _get_menu_by_status_item_id(self, item_id):
        plugin_server = application.server['plugin']
        for plugin_name in plugin_server.plugins:
            plugin = plugin_server.plugins[plugin_name]
            for status_item in plugin.status:
                if status_item.id == item_id:
                    menu_list = [menu_item.json() for menu_item in status_item.get_menu()]
                    return application.make_ok_response(data=menu_list)
        return application.make_fail_response(f'Status item not found, id={item_id}')
