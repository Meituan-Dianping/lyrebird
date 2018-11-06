from flask_restful import Resource
from lyrebird.mock import context
from flask import jsonify


class Status(Resource):

    def get(self):
        conf = context.application.conf
        return context.make_ok_response(
            **{'ip':conf.get('ip', 'unknown ip'), 
            'mock.port':conf['mock.port'], 
            'proxy.port':conf['proxy.port']})


class WorkMode(Resource):

    def put(self, mode=None):
        if context.Mode.contains(mode):
            context.application.work_mode = mode
            return context.make_ok_response()
        else:
            return context.make_fail_response(f'Unknown mode: {mode}')

    def get(self):
        return jsonify({'mode': context.application.work_mode})
