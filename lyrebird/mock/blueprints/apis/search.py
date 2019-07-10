from flask_restful import Resource
from lyrebird.mock import context
from lyrebird import application


class SearchMockDataByName(Resource):

    def get(self, search_str=None):
        _matched_group = []
        for _id in context.application.data_manager.id_map:
            group = context.application.data_manager.id_map.get(_id)
            if not search_str and group.get('name') and group.get('type') == 'group':
                _matched_group.append({
                    'id': group['id'],
                    'name': group['name'],
                    'parent_id': group['parent_id']
                })
            elif search_str and search_str in group.get('name', '') and group.get('type') == 'group':
                _matched_group.append({
                    'id': group['id'],
                    'name': group['name'],
                    'parent_id': group['parent_id']
                })
        for _group in _matched_group:
            _abs_path = context.application.data_manager._get_abs_parent_path(_group)
            _group['abs_parent_path'] = _abs_path
        return application.make_ok_response(data=_matched_group)
