from flask_restful import Resource
from lyrebird.mock import context
from flask import request
from lyrebird import application
from ...handlers.encoder_decoder_handler import encoders_decoders


class MockGroup(Resource):
    """
    mock数据组
    """

    def get(self, group_id=None):
        if not group_id:
            root = context.application.data_manager.root
            return application.make_ok_response(data=root)

        # 返回数据组中数据列表
        _group = context.application.data_manager.id_map.get(group_id)
        if not _group:
            return context.make_fail_response('Not found group')

        return application.make_ok_response(data=_group)

    def post(self):
        name = request.json.get('name')
        parent_id = request.json.get('parent_id')
        group_id = context.application.data_manager.add_group(parent_id, name)
        return context.make_ok_response(data={'group_id': group_id})

    def put(self):
        group_id = request.json.get('id')
        data = request.json.get('data')
        context.application.data_manager.update_group(group_id, data)
        return context.make_ok_response()

    def delete(self, group_id):
        context.application.data_manager.delete(group_id)
        return context.make_ok_response()


class MockData(Resource):
    """
    mock数据
    """

    def get(self, _id):
        data = context.application.data_manager.get(_id)
        display_item = {}
        # Import decoder for decoding the requested content
        encoders_decoders.decoder_handler(data, output=display_item)
        return application.make_ok_response(data=display_item)

    def put(self):
        data_id = request.json.get('id')
        data = request.json
        # Import encoder for encoding the requested content
        encoders_decoders.encoder_handler(data)
        context.application.data_manager.update_data(data_id, data)
        return context.make_ok_response()

    def post(self):
        parent_id = request.json.get('parent_id')
        data = request.json.get('data')
        new_data_id = context.application.data_manager.add_data(parent_id, data)
        return context.make_ok_response(data_id=new_data_id)

    def delete(self, _id):
        context.application.data_manager.delete(_id)
        return context.make_ok_response()


class ActivatedMockGroup(Resource):

    def get(self):
        return context.make_ok_response(
            data=context.application.data_manager.activated_group
        )

    def put(self, group_id=None, action=None):
        if action == 'activate':
            # Only one group could be activated
            context.application.data_manager.deactivate()
            context.application.data_manager.activate(group_id)
        else:
            context.application.data_manager.deactivate()
        return context.make_ok_response()


class MockGroupByName(Resource):

    def put(self):
        group_name = request.json.get('group_name')
        action = request.json.get('action', 'activate')
        for _id in context.application.data_manager.id_map:
            group = context.application.data_manager.id_map.get(_id)
            if group['name'] == group_name:
                if action == 'activate':
                    context.application.data_manager.deactivate()
                    context.application.data_manager.activate(group['id'])
                else:
                    context.application.data_manager.deactivate()
                return context.make_ok_response()
        return context.make_fail_response(f'Group not found. name={group_name}')
