from flask_restful import Resource
from flask import request
from lyrebird.mock import context, headers
from lyrebird import application
from lyrebird.event_filter import Filter
from lyrebird.application import config
from urllib.parse import urlencode, unquote
from flask import request, Response
from copy import deepcopy
from lyrebird.utils import url_decode
import json


class Flow(Resource):
    """
    当前请求单条数据
    """

    def get(self, id):
        is_origin = request.args.get('is_origin', 'false').strip().lower() == 'true'
        no_decode = request.args.get('no_decode')
        if no_decode is None:
            no_decode = config.get('inspector.detail.no_decode', 0)
        if isinstance(no_decode, str) and no_decode.strip().isdigit():
            no_decode = int(no_decode)
        elif not isinstance(no_decode, int):
            return application.make_fail_response(f'Param no_decode type error, in the request of api/flow/{id}')
        
        for item in context.application.cache.items():
            if item['id'] == id:
                # Import decoder for decoding the requested content
                display_item = {}
                if is_origin:
                    display_item = deepcopy(item)
                else:
                    application.encoders_decoders.decoder_handler(item, output=display_item)
                if not no_decode:
                    for key in ('url', 'path', 'query'):
                        url_decode(display_item['request'], key)
                return application.make_ok_response(data=display_item)
        return application.make_fail_response(f'Request {id} not found')


def get_flow_list_by_filter(filter_obj):
    all_items = context.application.cache.items()[::-1]
    req_list = []
    target_items = Filter.get_items_after_filtration(all_items, filter_obj)
    for item in target_items:
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
            )if item.get('response') and len(item.get('response').keys()) > 1 else {},
            action=item.get('action', [])
        )
        # Add key `request.port` when port is not default
        if item['request'].get('port') not in ['443', '80']:
            info['request']['port'] = item['request'].get('port')

        # Add key `proxy_response` into info only if item contains proxy_response
        if item.get('proxy_response'):
            info['proxy_response'] = {
                'code': item['proxy_response']['code']
            }
        # Change status
        if item['request']['headers'].get(headers.MITMPROXY_COMMAND):
            info['status'] = item['request']['headers'][headers.MITMPROXY_COMMAND]
        # SSR
        if item['request']['headers'].get('lyrebird') == 'mock':
            info['status'] = 'ssr'

        req_list.append(info)
    return req_list


class FlowList(Resource):
    """
    当前请求列表
    """

    def get(self):
        default_filter = context.application.selected_filter
        req_list = get_flow_list_by_filter(default_filter)
        return Response(json.dumps(req_list, ensure_ascii=False), mimetype='application/json', status=200)

    def delete(self):
        _ids = request.json.get('ids')
        if _ids:
            context.application.cache.delete_by_ids(*_ids)
        else:
            context.application.cache.clear()
        context.application.socket_io.emit('action', 'delete flow log')
        return application.make_ok_response()

    def post(self, action):
        if action == 'save':
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
        elif action == 'search':
            filter_name = request.json.get('selectedFilter')
            filter_obj = context.application.get_and_update_selected_filter_by_name(filter_name)
            req_list = get_flow_list_by_filter(filter_obj)
            return Response(json.dumps(req_list, ensure_ascii=False), mimetype='application/json', status=200)
        else:
            return application.make_fail_response(f'action: {action} is not supported')
