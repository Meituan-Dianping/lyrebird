from flask_restful import Resource
from lyrebird.mock import context
from flask import request
import traceback
from lyrebird import application, log
from lyrebird.config import CONFIG_TREE_LOAD_CHILDREN_ASYNC

logger = log.get_logger()

'''
1. new API
2. origin API, response add new key {data: {'name': '...'}} -> {data: {'name': '...'}, 'custom': [ {}, {} ]}
3. origin API response, frontend store add new prop
4. origin API response store, add DataDeteilFolder.vue computed prop
5. origin API response store DataDeteilFolder.vue, add DataDetailInfo.vue type

'''

class TreeView(Resource):
    def get(self):
        data = context.application.data_manager.get_tree()
        return application.make_ok_response(data=data)

    def post(self):
        data = request.json.get('tree')
        if not application.config.get('datamanager.v2.enable'):
            context.application.data_manager.tree = data
        return context.make_ok_response()

class OpenNodes(Resource):
    def get(self):
        data = context.application.data_manager.get_open_nodes()
        return application.make_ok_response(data=data)
    
    def post(self):
        data = request.json.get('openNodes')
        context.application.data_manager.save_open_nodes(data)
        return context.make_ok_response()

class MockGroup(Resource):
    """
    mock数据组
    """

    def get(self, group_id=None, label=None):
        query = request.args
        if group_id:
            if group_id == 'tmp_group':
                _group = None
                _group = context.application.data_manager.temp_mock_tree.get()
                return application.make_ok_response(data=_group)

            if query and query.get('childrenOnly') == 'true':
                children = context.application.data_manager._get_group_children(group_id) or []
                return application.make_ok_response(data=children)

            _group = context.application.data_manager.get_group(group_id)
            if not _group:
                return context.make_fail_response('Not found group')

            return application.make_ok_response(data=_group)
        
        if application.config.get('datamanager.v2.enable'):
            reset = False
            if query and query.get('reset') == 'true':
                reset = True
            context.application.data_manager.reload(reset)
            root = context.application.data_manager.root
            return application.make_ok_response(data=root)

        context.application.data_manager.reload()

        if label and not application.config.get('datamanager.v2.enable'):
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

        if application.config.get(CONFIG_TREE_LOAD_CHILDREN_ASYNC) and not application.config.get('datamanager.v2.enable'):
            # Although async, reload is needed
            data_map = context.application.data_manager.root_without_children()
            context.application.data_manager.tree = [data_map]
            context.application.data_manager.open_nodes = [data_map['id']]
            return application.make_ok_response(data=data_map)

        root = context.application.data_manager.root
        return application.make_ok_response(data=root)

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
        if 'query' in request.json:
            query = request.json['query']
            if query is None:
                return application.make_fail_response(f'Update query is None!')

            data = request.json.get('data')
            message = context.application.data_manager.update_by_query(query, data)

        else:
            group_id = request.json.get('id')
            data = request.json.get('data')
            message = context.application.data_manager.update_group(group_id, data)

        if message:
            return context.make_ok_response(**message)
        return context.make_ok_response()

    def delete(self, group_id=None):
        if group_id is not None:
            context.application.data_manager.delete(group_id)
            return context.make_ok_response()

        query = request.json.get('query')
        if query is None:
            return application.make_fail_response(f'Delete query is None!')

        if query.get('parent_id') == 'tmp_group':
            context.application.data_manager.temp_mock_tree.delete_by_query(query)
            return context.make_ok_response()

        if context.application.data_manager.is_deleting_lock:
            return application.make_fail_response(f'Is deleting, no new delete')

        context.application.data_manager.is_deleting_lock = True
        try:
            context.application.data_manager.delete_by_query(query)
        except Exception as e:
            logger.error(f'Delete error: {traceback.format_exc()}')
            return application.make_fail_response(f'Delete failure: {str(e)}')
        finally:
            context.application.data_manager.is_deleting_lock = False

        context.application.data_manager.reactive()
        return context.make_ok_response()


class MockData(Resource):
    """
    mock数据
    """

    def get(self, _id):
        data = context.application.data_manager.get_data(_id)
        display_item = {}
        # Import decoder for decoding the requested content
        application.encoders_decoders.decoder_handler(data, output=display_item)
        return application.make_ok_response(data=display_item)

    def put(self):
        data_id = request.json.get('id')
        data = request.json
        # Import encoder for encoding the requested content
        application.encoders_decoders.encoder_handler(data)
        if 'lyrebirdInternalFlow' in data:
            del data['lyrebirdInternalFlow']
        context.application.data_manager.update_data(data_id, data)
        context.application.data_manager.reactive()
        return context.make_ok_response()

    def post(self):
        parent_id = request.json.get('parent_id')
        data = request.json.get('data')

        if parent_id == 'tmp_group':
            new_data_id = context.application.data_manager.temp_mock_tree.add_data(data)
            return application.make_ok_response(data_id=new_data_id)

        new_data_id = context.application.data_manager.add_data(parent_id, data)
        return context.make_ok_response(data_id=new_data_id)

    def delete(self, _id):
        context.application.data_manager.delete(_id)
        return context.make_ok_response()


class ActivatedMockGroup(Resource):

    def get(self):
        if request.path == '/api/mock/activated':
            data = context.application.data_manager.activated_group
        elif request.path == '/api/mock/activated/flow':
            data = context.application.data_manager.activated_data
        else:
            data = {}
        return context.make_ok_response(data=data)

    def put(self, group_id=None, action=None):
        if action == 'activate':
            # Only one group could be activated
            if request.is_json:
                try:
                    info = request.json.get('info')
                    context.application.data_manager.activate(group_id, info=info)
                except Exception:
                    # If a request have json content-type but dose not have body.
                    # Handle flask exception when parse json failed.
                    context.application.data_manager.activate(group_id)
            else:
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
        application.reporter.report({
            'action': 'label.get'
        })
        if application.config.get('datamanager.v2.enable'):
            return application.make_ok_response(labels={})
        application.labels.get_label(context.application.data_manager.root)
        return application.make_ok_response(labels=application.labels.label_map)

    def post(self):
        application.reporter.report({
            'action': 'label.post'
        })
        if application.config.get('datamanager.v2.enable'):
            return application.make_fail_response('Label function has been deprecated.')
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
        application.reporter.report({
            'action': 'label.put'
        })
        if application.config.get('datamanager.v2.enable'):
            return application.make_fail_response('Label function has been deprecated.')
        label = request.json.get('label')
        label_id = label.get('id')
        if not label_id:
            return application.make_fail_response('Label id is required!')
        if not label_id in application.labels.label_map:
            return application.make_fail_response(f'Label {label.get("name")} not found!')

        application.labels.update_label(label)
        return context.make_ok_response()

    def delete(self):
        application.reporter.report({
            'action': 'label.delete'
        })
        if application.config.get('datamanager.v2.enable'):
            return application.make_fail_response('Label function has been deprecated.')
        label_id = request.json.get('id')
        if not label_id:
            return application.make_fail_response('Label id is required!')
        if not label_id in application.labels.label_map:
            return application.make_fail_response(f'Label {label_id} not found!')

        application.labels.delete_label(label_id)
        return context.make_ok_response()
