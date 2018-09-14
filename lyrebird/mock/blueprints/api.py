from lyrebird.mock import context
from lyrebird import application
from lyrebird.mock.filesystem import DataGroupConfBuilder
from flask import Blueprint, request, jsonify, abort
from flask_restful import Resource, Api
import json
import traceback
import time
from urllib.parse import urlparse, unquote
from lyrebird.mock.filesystem import DataHelper
from .. import plugin_manager

"""
实现控制API
"""

api = Blueprint('api', __name__, url_prefix='/api')
api_source = Api(api)


class Status(Resource):

    def get(self):
        conf = context.application.conf
        return context.make_ok_response(
            **{'ip':conf.get('ip', 'unknown ip'), 
            'mock.port':conf['mock.port'], 
            'proxy.port':conf['proxy.port']})


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
            info = dict()
            info['id'] = item['id']
            info['time'] = item['time']
            info['response-time'] = item['response-time']
            info['request'] = dict()
            info['request']['url'] = item['request']['url']
            info['request']['method'] = item['request']['method']
            info['response'] = dict()
            info['response']['code'] = item['response']['code']
            info['response']['mock'] = item['response']['headers'].get('lyrebird', 'proxy')
            req_list.append(info)
        return jsonify(req_list)

    def delete(self):
        _ids = request.form.getlist('ids')
        if _ids:
            context.application.cache.delete_by_ids(_ids)
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
        current_group = context.application.data_manager.current_data_group
        for item in record_items:
            current_group.add_data_and_filter(item)
        return context.make_ok_response()


class MockGroup(Resource):
    """
    mock数据组
    """
    def get(self, group=None):
        if not group:
            return jsonify([group_name for group_name in context.application.data_manager.data_groups])

        # 返回数据组中数据列表
        _group = context.application.data_manager.data_groups.get(group)
        if not _group:
            return context.make_fail_response('Not found group')

        data_list = []
        for k in _group.data_dict:
            data = _group.data_dict[k]

            _filter = None
            for req_filter in _group.conf['filters']:
                if req_filter['response'] == data.name:
                    _filter = req_filter['contents']
                    break

            data.read_file()
            data_list.append({
                'name': data.name,
                'url': data.json_data['request']['url'],
                'rule': {
                    'contains': _filter
                }
            })
        
        return jsonify(data_list)

    def post(self):
        name = request.form.get('name')
        data = request.form.get('data')
        origin_name = request.form.get('origin_name')
        if not name or not data:
            return abort('请设置form：name data')
        if origin_name == '':
            # todo json exception and origin_name exception
            context.application.data_manager.add_group(name, json.loads(data))
        else:
            # todo move to update method
            context.application.data_manager.update_group(origin_name, name, json.loads(data))
        return context.make_ok_response()

    def put(self):
        # todo
        return 'MockGroup UPDATE'

    def delete(self, group):
        if group in context.application.data_manager.data_groups:
            _group = context.application.data_manager.data_groups.pop(group)
            _group.delete()
            return context.make_ok_response()
        else:
            return context.make_fail_response('Not found group')


class MockData(Resource):
    """
    mock数据
    """
    def get(self, group=None, data=None):
        if not group or not data:
            return abort(400, '请设置参数 group name')
        _group = context.application.data_manager.data_groups.get(group)
        if _group and data in _group.data_dict:
            _data = _group.data_dict[data]
            _data.read_file()
            base_data = _data.json_data
            contains = []
            for req_filter in _group.conf['filters']:
                if req_filter['response'] == data:
                    contains = req_filter['contents']
            base_data['rule'] = {'contains': contains}
            return jsonify(base_data)
        return context.make_fail_response('Data not found')

    def put(self, group=None, data=None):
        
        return 'MockData UPDATE'

    def post(self, group=None, data=None):
        group = request.form.get('group')
        name = request.form.get('name')
        req = request.form.get('req')
        req_data = request.form.get('req_data')
        resp = request.form.get('resp')
        resp_data = request.form.get('resp_data')
        origin_name = request.form.get('origin_name')
        if not group or not name:
            return context.make_fail_response('请设置form：group & name')
        _group = context.application.data_manager.data_groups.get(group)
        if _group:
            data = DataHelper.to_dict(req, req_data, resp, resp_data)
            if origin_name == '' or origin_name is None:
                _group.add_data(name, data)
            else:
                _group.update_data(origin_name, name, data)
            return context.make_ok_response()
        else:
            return context.make_fail_response('Group not found')

    def delete(self, group=None, data=None):
        if not group or not data:
            return abort(400, '请设置参数 group name')
        _group = context.application.data_manager.data_groups.get(group)
        if _group and data in _group.data_dict:
            data = _group.data_dict[data]
            data.delete()
            _group.scan()
            return context.make_ok_response()
        return context.make_fail_response('Data not found')


class ActivatedMockGroup(Resource):

    def get(self):
        _current_data_group = context.application.data_manager.current_data_group
        if _current_data_group:
            return jsonify({'name': _current_data_group.name})
        else:
            return jsonify({'name': None})

    def put(self, group=None, action=None):
        if action == 'activate':
            result = context.application.data_manager.set_current_data_group(group)
        else:
            result = context.application.data_manager.set_current_data_group(None)
        if result:
            return context.make_ok_response()
        else:
            return context.make_fail_response("Activate group fail. Not found! group=%s action=%s" % (group, action))


class Conf(Resource):
    """
    Lyrebird 及 插件 配置文件获取和修改
    """

    def get(self, plugin_name):
        if plugin_name == 'lyrebird':
            return jsonify(application.config.raw())
        else:
            return jsonify(plugin_manager.get_conf(plugin_name))

    def put(self, plugin_name):
        try:
            if plugin_name == 'lyrebird':
                context.application.conf = request.get_json()
                context.application.save()
                return context.make_ok_response()
            else:
                plugin_manager.set_conf(plugin_name, request.get_json())
                return context.make_ok_response()
        except Exception as e:
            return context.make_fail_response(str(e))


class ResetConf(Resource):
    """
    Lyrebird 及 插件 配置文件重置
    """
    def put(self, plugin_name):
        try:
            if plugin_name == 'lyrebird':
                return context.make_fail_response('暂未开放')
            else:
                plugin_manager.set_default_conf(plugin_name)
                return context.make_ok_response()
        except Exception as e:
            return context.make_fail_response(str(e))


class WorkMode(Resource):

    def put(self, mode=None):
        if context.Mode.contains(mode):
            context.application.work_mode = mode
            return context.make_ok_response()
        else:
            return context.make_fail_response(f'Unknown mode: {mode}')

    def get(self):
        return jsonify({'mode': context.application.work_mode})

api_source.add_resource(Status, '/status')
api_source.add_resource(Flow, '/flow/<string:id>')
api_source.add_resource(FlowList, '/flow')
api_source.add_resource(MockGroup, '/mock', '/mock/<string:group>')
api_source.add_resource(MockData, '/mock/<string:group>/data', '/mock/<string:group>/data/<string:data>')
api_source.add_resource(ActivatedMockGroup, '/mock/activated', '/mock/<string:group>/<string:action>')
api_source.add_resource(Conf, '/conf/<string:plugin_name>')
api_source.add_resource(ResetConf, '/conf/<string:plugin_name>/reset')
api_source.add_resource(WorkMode, '/mode', '/mode/<string:mode>')