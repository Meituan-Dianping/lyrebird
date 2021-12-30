from flask_restful import Resource
from lyrebird import application


class StatusBar(Resource):

    def get(self, item_id=None):
        if item_id == None:
            return self._get_all_status_item()
        else:
            return self._get_menu_by_status_item_name(item_id)

    def _get_all_status_item(self):
        status_dict = {}

        plugin_server = application.server['plugin']
        for plugin in plugin_server.plugins.values():
            for status_item in plugin.status:
                if status_item.placement not in status_dict:
                    status_dict[status_item.placement] = []
                status_detail = status_item.json()
                status_dict[status_item.placement].append(status_detail)

        for status_list in status_dict.values():
            status_list.sort(key=lambda x:x['rank'], reverse=True)
        return application.make_ok_response(**status_dict)

    def _get_menu_by_status_item_name(self, name):
        plugin_server = application.server['plugin']
        for plugin in plugin_server.plugins.values():
            for status_item in plugin.status:
                if status_item.name != name:
                    continue

                menu_list = status_item.get_detail()
                return application.make_ok_response(data=menu_list)

        return application.make_fail_response(f'Status item not found, id={name}')
