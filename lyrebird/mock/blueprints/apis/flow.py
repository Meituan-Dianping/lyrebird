from flask_restful import Resource
from lyrebird.mock import context
from lyrebird import application
from urllib.parse import urlencode, unquote
from flask import request
import json


class Flow(Resource):
    """
    当前请求单条数据
    """

    def get(self, id):
        for item in context.application.cache.items():
            if item['id'] == id:
                # Import decoder for decoding the requested content
                display_item = {}
                application.encoders_decoders.decoder_handler(item, output=display_item)
                return application.make_ok_response(data=display_item)
        return application.make_fail_response(f'Request {id} not found')


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
                    scheme=item['request'].get('scheme'),
                    host=item['request'].get('host'),
                    path=item['request'].get('path'),
                    params=unquote(urlencode(item['request']['query'])),
                    method=item['request'].get('method')
                ),
                response=dict(
                    code=item['response']['code'],
                    mock=item['response']['headers'].get('lyrebird', 'proxy'),
                    modified=item['request']['headers'].get('lyrebird_modified') or item['response']['headers'].get('lyrebird_modified', '')
                )if item.get('response') else {},
                action=item.get('action', [])
            )
            # Add key `proxy_response` into info only if item contains proxy_response
            if item.get('proxy_response'):
                info['proxy_response'] = {
                    'code': item['proxy_response']['code']
                }
            req_list.append(info)

        def gen():
            yield json.dumps(req_list, ensure_ascii=False)
        return application.make_streamed_response(gen)

    def delete(self):
        _ids = request.json.get('ids')
        if _ids:
            context.application.cache.delete_by_ids(*_ids)
        else:
            context.application.cache.clear()
        context.application.socket_io.emit('action', 'delete flow log')
        return application.make_ok_response()

    def post(self):
        _ids = request.json.get('ids')
        record_items = []
        for _id in _ids:
            for item in context.application.cache.items():
                if _id == item['id']:
                    record_items.append(item)
                    break
        dm = context.application.data_manager

        for flow in record_items:
            dm.save_data(flow)

        return application.make_ok_response()
