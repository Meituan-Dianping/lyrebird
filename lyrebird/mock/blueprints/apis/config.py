from flask_restful import Resource
from lyrebird.mock import context, plugin_manager
from flask import request, jsonify, abort
from lyrebird import application


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
