from flask_restful import Resource
from lyrebird.mock import context
from flask import request
from lyrebird import application, log

logger = log.get_logger()


class MockGroup(Resource):
    """
    mock数据组
    """

    def get(self, group_id=None, label=None):
        if group_id:
            _group = context.application.data_manager.id_map.get(group_id)
            if not _group:
                return context.make_fail_response('Not found group')

            return application.make_ok_response(data=_group)

        context.application.data_manager.reload()
        root = context.application.data_manager.root
        if not label:
            return application.make_ok_response(data=root)

        # update mock data tree with label
        groups_set = set()

        label_list = label.split('+')
        for label_id in label_list:
            label = application.labels.label_map.get(label_id)
            if not label:
                return application.make_fail_response(f'Label {label_id} is not found!')

            if not groups_set:
                groups_set = set(label['groups'])
            else:
                groups_set = groups_set & set(label['groups'])

        data_map = context.application.data_manager.make_data_map_by_group(groups_set)
        return application.make_ok_response(data=data_map)


    def post(self):
        data = request.json.get('data')
        if not data:
            data = {
                'name': request.json.get('name'),
                'parent_id': request.json.get('parent_id')
            }
        group_id = context.application.data_manager.add_group(data)
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
        application.encoders_decoders.decoder_handler(data, output=display_item)
        return application.make_ok_response(data=display_item)

    def put(self):
        data_id = request.json.get('id')
        data = request.json
        # Import encoder for encoding the requested content
        application.encoders_decoders.encoder_handler(data)
        context.application.data_manager.update_data(data_id, data)
        context.application.data_manager.reactive()
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
            context.application.data_manager.activate(group_id)
        elif action == 'deactivate':
            context.application.data_manager.deactivate()
        else:
            logger.warning('DeprecationWarning: Deactivate with no action parameter is deprecated soon,\
                use /mock/<string:group_id>/deactivate instead')
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
                    context.application.data_manager.activate(group['id'])
                elif action == 'deactivate':
                    context.application.data_manager.deactivate()
                else:
                    logger.warning('DeprecationWarning: Deactivate with no action parameter is deprecated soon,\
                        use /mock/<string:group_id>/deactivate instead')
                    context.application.data_manager.deactivate()
                return context.make_ok_response()
        return context.make_fail_response(f'Group not found. name={group_name}')


class MockDataLabel(Resource):
    """
    mock数据标签
    """

    def get(self):
        application.labels.get_label(context.application.data_manager.root)
        return application.make_ok_response(labels=application.labels.label_map)

    def post(self):
        label = request.json.get('label')
        required_key = ['name']
        missed_required_key = [key for key in required_key if not label.get(key)]
        if missed_required_key:
            return application.make_fail_response(f'Label {" ".join(missed_required_key)} is required!')

        label_id = application.labels._get_label_name_md5(label)
        if label_id in application.labels.label_map:
            return application.make_fail_response(f'Label {label["name"]} existed!')

        application.labels.create_label(label)
        return context.make_ok_response()

    def put(self):
        label = request.json.get('label')
        label_id = label.get('id')
        if not label_id:
            return application.make_fail_response('Label id is required!')
        if not label_id in application.labels.label_map:
            return application.make_fail_response(f'Label {label.get("name")} not found!')

        application.labels.update_label(label)
        return context.make_ok_response()

    def delete(self):
        label_id = request.json.get('id')
        if not label_id:
            return application.make_fail_response('Label id is required!')
        if not label_id in application.labels.label_map:
            return application.make_fail_response(f'Label {label_id} not found!')

        application.labels.delete_label(label_id)
        return context.make_ok_response()
