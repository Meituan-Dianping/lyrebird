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
                'parent_id': _group['parent_id']
            })

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
                if group.get('type') == 'group' and group.get('name') and group.get('name') != '$':
                    _add_group(group)
        for _group in _matched_group:
            _abs_path = context.application.data_manager._get_abs_parent_path(_group)
            _group['abs_parent_path'] = _abs_path
        return application.make_ok_response(data=_matched_group)
