from flask_restful import Resource
from lyrebird.mock import context
from lyrebird import application
from flask import request, jsonify, abort, stream_with_context
import json
import time
from ...handlers.encoder_decoder_handler import encoders_decoders


class Flow(Resource):
    """
    当前请求单条数据
    """

    def get(self, id):
        for item in context.application.cache.items():
            if item['id'] == id:
                display_item = {}
                encoders_decoders.decoder_handler(item, res=display_item)
                return application.make_ok_response(data=display_item)
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
                    mock=item['response']['headers'].get('lyrebird', 'proxy'),
                    modified=item['request']['headers'].get('lyrebird_modified') or item['response']['headers'].get('lyrebird_modified', '')
                )if item.get('response') else {}
            )
            req_list.append(info)

        def gen():
            yield json.dumps(req_list, ensure_ascii=False)
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

        flow_list = context.application.cache.items()
        for flow in flow_list:
            if flow['id'] in _ids:
                dm.save_data(flow)

        return context.make_ok_response()
