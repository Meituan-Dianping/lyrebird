from flask_restful import Resource
from lyrebird.mock import context, headers
from lyrebird import application
from lyrebird import utils
from urllib.parse import urlencode, unquote
from flask import request, Response
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
        ignore_host = context.application.selected_filter.get('ignore', []) if context.application.selected_filter else []
        all_items = context.application.cache.items()[::-1]
        req_list = []
        for item in all_items:
            is_ignore = utils.is_target_match_patterns(ignore_host, item['request'].get('host'))
            if is_ignore:
                continue
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
            # Change status
            if item['request']['headers'].get(headers.MITMPROXY_COMMAND):
                info['status'] = item['request']['headers'][headers.MITMPROXY_COMMAND]
            req_list.append(info)

        return Response(json.dumps(req_list, ensure_ascii=False), mimetype='application/json', status=200)

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


class FlowFilter(Resource):

    def get(self):
        filters = context.application.filters
        selected_filter = context.application.selected_filter
        return application.make_ok_response(selected_filter=selected_filter, filters=filters)

    def put(self):
        selected_filter_name = request.json.get('name')
        if not selected_filter_name:
            context.application.selected_filter = None
            return application.make_ok_response()

        for f in context.application.filters:
            if f['name'] == selected_filter_name:
                context.application.selected_filter = f
                return application.make_ok_response()

        return application.make_fail_response(f'Flow filter {selected_filter_name} not found!')
