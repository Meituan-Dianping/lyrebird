from flask_restful import Resource
from lyrebird.mock import context
from flask import request, jsonify
from lyrebird import application


class Conf(Resource):
    """
    Lyrebird 及 插件 配置文件获取和修改
    """

    # 配置中一旦初始化就不能修改的字段列表
    CONST_CONFIG_FIELDS = set(["version", "proxy.port", "mock.port", "ip"])

    def get(self):
        return jsonify(application.config.raw())

    def put(self):
        try:
            context.application.conf = request.get_json()
            context.application.save()
            return context.make_ok_response()
        except Exception as e:
            return context.make_fail_response(str(e))

    def patch(self):
        try:
            update_conf = request.get_json()
            if update_conf is None:
                return context.make_fail_response("request content type must be 'application/json'.")
            
            union_Fields = self.CONST_CONFIG_FIELDS & update_conf.keys()
            if len(union_Fields) > 0:
                return context.make_fail_response("配置中%s字段禁止修改" % union_Fields)
            else:
                old_conf = application.config.raw()
                old_conf.update(update_conf)
                context.application.conf = old_conf
                context.application.save()
                return context.make_ok_response()
        except Exception as e:
            return context.make_fail_response(str(e))
