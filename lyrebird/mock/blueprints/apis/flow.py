from flask_restful import Resource
from lyrebird.mock import context
from flask import request, jsonify, abort, stream_with_context
import json
import time


class Flow(Resource):
    """
    当前请求单条数据
    """
    def get(self, id):
        for item in context.application.cache.items():
            if item['id'] == id:
                return jsonify(item)
        return abort(400, 'Request not found')


class FlowList(Resource):
    """
    当前请求列表
    """
    def get(self):
        all_items = context.application.cache.items()[::-1]
        req_list = []
        for item in all_items:
            info = dict(
                id=item['id'],
                size=item['size'],
                duration=item['duration'],
                start_time=item['start_time'],
                request=dict(
                    url=item['request'].get('url'),
                    path=item['request'].get('path'),
                    host=item['request'].get('host'),
                    method=item['request'].get('method')
                    ),
                response=dict(
                    code=item['response']['code'],
                    mock=item['response']['headers'].get('lyrebird', 'proxy')
                    )if item.get('response') else {}
                )
            req_list.append(info)
        def gen():
            yield json.dumps(req_list)
        return context.make_streamed_response(gen)

    def delete(self):
        _ids = request.json.get('ids')
        if _ids:
            context.application.cache.delete_by_ids(*_ids)
        else:
            context.application.cache.clear()
        context.application.socket_io.emit('action', 'delete flow log')
        return context.make_ok_response()

    def post(self):
        _ids = request.json.get('ids')
        record_items = []
        for _id in _ids:
            for item in context.application.cache.items():
                if _id == item['id']:
                    record_items.append(item)
                    break
        dm = context.application.data_manager
        activated_group = dm.groups.get(dm.activated_group_id)
        if not activated_group:
            return context.make_fail_response('Not activate any group')

        flow_list = context.application.cache.items()
        for flow in flow_list:
            if flow['id'] in _ids:
                data = activated_group.create_data(flow=flow)
                data.save()

        dm.router.switch_group(activated_group)

        return context.make_ok_response()
