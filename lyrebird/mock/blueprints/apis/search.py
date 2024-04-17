from flask_restful import Resource
from lyrebird.mock import context
from lyrebird import application
from flask import request


class SearchMockData(Resource):

    # adapt to V1
    def _getV1(self, search_str=None):
        _matched_group = []

        def _add_group(_group):
            _matched_group.append({
                'id': _group['id'],
                'name': _group['name'],
                'type': _group['type'],
                'parent_id': _group['parent_id'],
                'abs_parent_path': _get_abs_parent_path(_group),
                'abs_parent_obj': _get_abs_parent_obj(_group)
            })

        def _get_abs_parent_path(_group):
            _abs_parent_path = context.application.data_manager._get_abs_parent_path(_group)
            return _abs_parent_path

        def _get_abs_parent_obj(_group):
            _abs_parent_obj = context.application.data_manager._get_abs_parent_obj(_group)
            return _abs_parent_obj

        if search_str:
            if context.application.data_manager.id_map.get(search_str):
                # search_str is group id
                group = context.application.data_manager.id_map.get(search_str)
                _add_group(group)
            else:
                for _id, group in context.application.data_manager.id_map.items():
                    if group.get('type') == 'group' and search_str.lower() in group.get('name', '').lower():
                        _add_group(group)
        else:
            for _id, group in context.application.data_manager.id_map.items():
                if group.get('type') == 'group' and group.get('name'):
                    _add_group(group)
        return application.make_ok_response(data=_matched_group)

    def get(self, search_str=None):
        query = request.args
        sender = None
        if query and query.get('sender'):
            sender = query.get('sender')
        if query and query.get('search_str'):
            search_str = query.get('search_str')
        if application.config.get('datamanager.v2.enable'):
            data = context.application.data_manager.search(search_str, sender)
            return application.make_ok_response(data=data)
        else:
            return self._getV1(search_str)

    def post(self):
        #search_by_open_nodes
        open_nodes = request.json.get('open_nodes', [])
        reset = request.json.get('reset', False)
        data = context.application.data_manager.reload(reset, open_nodes)
        return application.make_ok_response(data=data)

