from flask_restful import Resource
from lyrebird.mock import context
from flask import request
from lyrebird import utils
from lyrebird import version
from lyrebird import application


class Status(Resource):

    def get(self):
        # Lyrebird status contains: 'READY' and 'INITING'
        if application.status != 'READY':
            return context.make_fail_response('Lyrebird not ready')

        conf = context.application.conf
        return context.make_ok_response(
            **{'ip': conf.get('ip', 'unknown ip'),
               'mock.port': conf['mock.port'],
               'proxy.port': conf['proxy.port'],
               'extra.mock.port': conf['extra.mock.port'],
               'version': version.VERSION
               })


class Manifest(Resource):

    def get(self):
        conf = context.application.conf
        return context.make_ok_response(
            **{'manifest': conf.get('manifest', [])
               })


class WorkMode(Resource):

    def put(self, mode=None):
        if context.Mode.contains(mode):
            context.application.work_mode = mode
            return application.make_ok_response()
        else:
            return application.make_fail_response(f'Unknown record mode: {mode}')

    def get(self):
        return application.make_ok_response(data=context.application.work_mode)


class DiffMode(Resource):

    def put(self):
        is_diff_mode = request.json.get('status')
        context.application.is_diff_mode = is_diff_mode
        return application.make_ok_response()

    def get(self):
        return application.make_ok_response(diffmode=context.application.is_diff_mode)


class Render(Resource):

    def put(self):
        origin_data = request.json.get('data')
        enable_tojson = request.json.get('enable_tojson')
        data = utils.render(origin_data, enable_tojson)
        return context.make_ok_response(data=data)
