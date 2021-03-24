from flask_restful import Resource
from lyrebird.mock import context
from flask import request, jsonify
from lyrebird import application


class Conf(Resource):
    """
    Lyrebird 及 插件 配置文件获取和修改
    """

    def get(self):
        return jsonify(application.config.raw())

    def put(self):
        try:
            context.application.conf = request.get_json()
            context.application.save()
            return context.make_ok_response()
        except Exception as e:
            return context.make_fail_response(str(e))
