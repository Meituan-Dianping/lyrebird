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
        name = request.form.get('name')
        group = context.application.data_manager.create_group()
        group.name = name
        group.save()
        return context.make_ok_response(group_id=group.id)

    def put(self):
        name = request.form.get('name')
        group_id = request.form.get('group_id')
        group = context.application.data_manager.groups.get(group_id)
        if not group:
            return context.make_fail_response('Group not found')
        group.name = name
        group.save()
        return context.make_ok_response()

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
        _data = _group.get(data_id)
        if not _data:
            return context.make_fail_response('Data not found')

        prop = request.form.get('prop')
        req = request.form.get('request')
        req_data = request.form.get('request_data')
        resp = request.form.get('response')
        resp_data = request.form.get('response_data')

        _data.name = prop.get('name')
        _data.rule = prop.get('rule')
        if req:
            _data.request.content = req
        if req_data:
            _data.request_data.content = req_data
        if resp:
            _data.response.content = resp
        if resp_data:
            _data.response_data.content = resp_data
        _data.save()
        return context.make_ok_response()

    def post(self, group_id=None, data_id=None):
        group = request.form.get('group')
        name = request.form.get('name')
        req = request.form.get('req')
        req_data = request.form.get('req_data')
        resp = request.form.get('resp')
        resp_data = request.form.get('resp_data')
        origin_name = request.form.get('origin_name')
        if not group or not name:
            return context.make_fail_response('请设置form：group & name')
        
        _group = context.application.data_manager.groups.get(group)
        if not _group:
            return context.make_fail_response('Group not found')

        _data = _group.create_data()
        _data.name = name
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
            context.application.data_manager.deactivate(group_id)
        return context.make_ok_response()
