from flask_restful import Resource
from lyrebird.mock import context
from flask import request, jsonify, abort


class MockGroup(Resource):
    """
    mock数据组
    """
    def get(self, group_id=None):
        if not group_id:
            groups = context.application.data_manager.groups
            return jsonify([groups[group_id].json() for group_id in groups])

        # 返回数据组中数据列表
        _group = context.application.data_manager.groups.get(group_id)
        if not _group:
            return context.make_fail_response('Not found group')

        return jsonify(_group.json(detail=True))

    def post(self):
        name = request.json.get('name')
        parent = request.json.get('parent')
        group = context.application.data_manager.create_group()
        group.name = name
        group.parent_id = parent
        group.save()
        return context.make_ok_response(group_id=group.id)

    def put(self):
        name = request.json.get('name')
        group_id = request.json.get('id')
        parent = request.json.get('parent')
        group = context.application.data_manager.groups.get(group_id)
        if not group:
            return context.make_fail_response('Group not found')
        group.name = name
        group.parent_id = parent
        group.save()
        return context.make_ok_response(group_id=group.id)

    def delete(self, group_id):
        context.application.data_manager.delete_group(group_id)
        return context.make_ok_response()


class MockData(Resource):
    """
    mock数据
    """
    def get(self, group_id=None, data_id=None):
        if not group_id or not data_id:
            return abort(400, '请设置参数 group_id & data_id')
        _group = context.application.data_manager.groups.get(group_id)
        if not _group:
            return context.make_fail_response('Group not found')
        _data = _group.all_data.get(data_id)
        if not _data:
            return context.make_fail_response('Data not found')
        return jsonify(_data.json(detail=True))

    def put(self, group_id=None, data_id=None):
        if not group_id or not data_id:
            return abort(400, '请设置参数 group_id & data_id')
        _group = context.application.data_manager.groups.get(group_id)
        if not _group:
            return context.make_fail_response('Group not found')
        _data = _group.all_data.get(data_id)
        if not _data:
            return context.make_fail_response('Data not found')

        _data.name = request.json.get('name')
        _data.rule = request.json.get('rule')
        req = request.json.get('request')
        if req:
            _data.request.content = req['content']
            _data.request.filetype = req['filetype']
        req_data = request.json.get('request_data')
        if req_data:
            _data.request_data.content = req_data['content']
            _data.request_data.filetype = req_data['filetype']
        resp = request.json.get('response')
        if resp:
            _data.response.content = resp['content']
            _data.response.filetype = resp['filetype']
        resp_data = request.json.get('response_data')
        if resp_data:
            _data.response_data.content = resp_data['content']
            _data.response_data.filetype = resp_data['filetype']
        _data.save()
        return context.make_ok_response()

    def post(self, group_id=None, data_id=None):
        name = request.json.get('name')
        rule = request.json.get('rule')
        req = request.json.get('request')
        req_data = request.json.get('request_data')
        resp = request.json.get('response')
        resp_data = request.json.get('response_data')

        _group = context.application.data_manager.groups.get(group_id)
        if not _group:
            return context.make_fail_response(f'Group not found by id={group_id}')

        _data = _group.create_data()
        _data.name = name
        _data.rule = rule
        _data.request.content = req
        _data.request_data.content = req_data
        _data.response.content = resp
        _data.response_data.content = resp_data
        _data.save()
        return context.make_ok_response()

    def delete(self, group_id=None, data_id=None):
        _group = context.application.data_manager.groups.get(group_id)
        if not _group:
            return context.make_fail_response('Group not found')
        ids = request.json.get('ids')
        for data_id in ids:
            _group.delete_data(data_id)
        return context.make_ok_response()


class ActivatedMockGroup(Resource):

    def get(self):
        activated_group_id = context.application.data_manager.activated_group_id
        if not activated_group_id:
            return context.make_fail_response('No group was activated')
        group = context.application.data_manager.groups.get(activated_group_id)
        return context.make_ok_response(name=group.name, id=group.id)

    def put(self, group_id=None, action=None):
        if action == 'activate':
            context.application.data_manager.activate(group_id)
        else:
            context.application.data_manager.deactivate()
        return context.make_ok_response()


class MockGroupByName(Resource):

    def put(self):
        group_name = request.json.get('group_name')
        action = request.json.get('action', 'activate')
        for group_id in context.application.data_manager.groups:
            if group_name == context.application.data_manager.groups[group_id].name:
                if action == 'activate':
                    context.application.data_manager.activate(group_id)
                else:
                    context.application.data_manager.deactivate()
                return context.make_ok_response()
        return context.make_fail_response(f'Group not found. name={group_name}')
