from flask_restful import Resource
from lyrebird.mock import context
from flask import request, jsonify
from lyrebird import application


class Conf(Resource):
    """
    Lyrebird 及 插件 配置文件获取和修改
    """

    def get(self, conf_name=None):
        if not conf_name:
            return application.make_ok_response(config=application.config.raw())
        return application.make_ok_response(config=application.config.get(conf_name, ''))

    def put(self, conf_name):
        config_value = request.json.get('value')
        application.config.__setitem__(conf_name, config_value)
        return application.make_ok_response()

    def post(self):
        try:
            context.application.conf = request.get_json()
            context.application.save()
            return context.make_ok_response()
        except Exception as e:
            return context.make_fail_response(str(e))
