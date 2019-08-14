import codecs
from flask import request, jsonify
from flask_restful import Resource
from lyrebird import application
from lyrebird.mock import context


class Checker(Resource):
    def get(self, checker_id=None):
        if not checker_id:
            checkers = application.checkers
            return jsonify([checkers[checker_name].json() for checker_name in checkers])

        _checker = application.checkers.get(checker_id)
        if not _checker:
            return context.make_fail_response(f'Checker {checker_id} not found')

        checker = application.checkers[checker_id]
        with codecs.open(checker.path, 'r', 'utf-8') as f:
            content = f.read()
            return jsonify(content)

    def put(self, checker_id):
        _checker = application.checkers.get(checker_id)
        if not _checker:
            return context.make_fail_response(f'Checker {checker_id} not found')

        if 'status' not in request.json:
            return context.make_fail_response(f'Checker {checker_id} status not found')

        _checker_status = request.json.get('status')
        if _checker_status:
            application.checkers[checker_id].activate()
        else:
            application.checkers[checker_id].deactivate()
        return context.make_ok_response()
