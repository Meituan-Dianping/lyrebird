from flask_restful import Resource
from lyrebird.mock import context
from lyrebird import application


class SearchMockDataByName(Resource):

    def get(self, search_str=None):
        _matched_group = []
        if search_str:
            if context.application.data_manager.id_map.get(search_str):
                # search_str is group id
                group = context.application.data_manager.id_map.get(search_str)
                _matched_group.append({
                    'id': group['id'],
                    'name': group['name'],
                    'parent_id': group['parent_id']
                })
            else:
                for _id, group in context.application.data_manager.id_map.items():
                    if group.get('type') == 'group' and search_str.lower() in group.get('name', '').lower():
                        _matched_group.append({
                            'id': group['id'],
                            'name': group['name'],
                            'parent_id': group['parent_id']
                        })
        else:
            for _id in context.application.data_manager.id_map:
                group = context.application.data_manager.id_map.get(_id)
                if group.get('type') == 'group' and group.get('name') and group.get('name') != '$':
                    _matched_group.append({
                        'id': group['id'],
                        'name': group['name'],
                        'parent_id': group['parent_id']
                    })
        for _group in _matched_group:
            _abs_path = context.application.data_manager._get_abs_parent_path(_group)
            _group['abs_parent_path'] = _abs_path
        return application.make_ok_response(data=_matched_group)
