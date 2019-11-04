from flask_restful import Resource
from lyrebird.mock import context
from lyrebird import application


class SearchMockDataByName(Resource):

    def get(self, search_str=None):
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
