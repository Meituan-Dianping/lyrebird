from flask_restful import Resource
from lyrebird import application


class StatusBar(Resource):

    def get(self, item_id=None):
        if item_id == None:
            return self._get_all_status_item()
        else:
            return self._get_menu_by_status_item_name(item_id)

    def _get_all_status_item(self):
        status_item_ranked = []
        status_item_unranked = []
        plugin_server = application.server['plugin']
        for plugin_name in plugin_server.plugins:
            plugin = plugin_server.plugins[plugin_name]
            for status_item in plugin.status:
                if status_item.rank:
                    status_item_ranked.append({
                        'id': status_item.name,
                        'rank': status_item.rank,
                        'text': status_item.get_text()
                    })
                    continue
                status_item_unranked.append({
                    'id': status_item.name,
                    'text': status_item.get_text()
                })
        status_item_ranked.sort(key=lambda x:x['rank'])
        all_status_item = status_item_ranked + status_item_unranked
        return application.make_ok_response(data=all_status_item)

    def _get_menu_by_status_item_name(self, name):
        plugin_server = application.server['plugin']
        for plugin_name in plugin_server.plugins:
            plugin = plugin_server.plugins[plugin_name]
            for status_item in plugin.status:
                if status_item.name == name:
                    menu_list = [menu_item.json() for menu_item in status_item.get_menu()]
                    return application.make_ok_response(data=menu_list)
        return application.make_fail_response(f'Status item not found, id={name}')
