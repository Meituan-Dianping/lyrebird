from lyrebird.config import ConfigException
from flask_restful import Resource
from lyrebird.mock import context
from flask import request, jsonify
from lyrebird import application
from lyrebird import log

logger = log.get_logger()


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

    def patch(self):

        update_conf = request.get_json()
        if update_conf is None or not isinstance(update_conf, dict):
            return application.make_fail_response('Request body must be a JSONObject!')

        if not update_conf:
            logger.warning('This request cannot modify config, request body is empty.')
            return application.make_ok_response()

        try:
            application._cm.override_config_field(update_conf)
            return application.make_ok_response()
        except ConfigException as e:
            return application.make_fail_response(str(e))
