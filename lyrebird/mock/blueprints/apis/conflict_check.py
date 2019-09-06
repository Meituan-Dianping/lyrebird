from flask_restful import Resource
from lyrebird.mock import context
from lyrebird import application


class ConflictCheck(Resource):

    def get(self, group_id):
        result = context.application.data_manager.check_conflict(group_id)
        return application.make_ok_response(data=result)


class ActivatedDataConflictCheck(Resource):

    def get(self):
        result = context.application.data_manager.activated_data_check_conflict()
        return application.make_ok_response(data=result)
