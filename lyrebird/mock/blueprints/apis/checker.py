from flask import request
from flask_restful import Resource
from lyrebird import application


class Checker(Resource):
    def get(self, checker_id=None):
        if not checker_id:
            checkers = application.checkers
            script_info_list = [checkers[checker_name].json() for checker_name in checkers]
            script_info_list.sort(key=lambda x:x['name'])
            return application.make_ok_response(data=script_info_list)

        _checker = application.checkers.get(checker_id)
        if not _checker:
            return application.make_fail_response(f'Checker {checker_id} not found')

        content = _checker.read()
        return application.make_ok_response(data=content)

    def put(self, checker_id):
        _checker = application.checkers.get(checker_id)
        if not _checker:
            return application.make_fail_response(f'Checker {checker_id} not found')

        if 'status' not in request.json:
            return application.make_fail_response(f'Checker {checker_id} status not found')

        _checker_status = request.json.get('status')
        if _checker_status:
            application.checkers[checker_id].activate()
        else:
            application.checkers[checker_id].deactivate()
        return application.make_ok_response()

    def post(self, checker_id):
        _checker = application.checkers.get(checker_id)
        if not _checker:
            return application.make_fail_response(f'Checker {checker_id} not found')
        _checker_data = request.json.get('data')
        if not _checker_data:
            return application.make_fail_response(f'Checker {checker_id} data not found')

        origin_checker_detail = _checker.read()
        try:
            _checker.write(_checker_data)
        except Exception as e:
            _checker.write(origin_checker_detail)
            return application.make_fail_response(f'Save checker {checker_id} failure: {str(e)}')

        return application.make_ok_response()
