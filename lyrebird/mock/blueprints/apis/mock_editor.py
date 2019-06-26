from flask_restful import Resource
from lyrebird.mock import context
from lyrebird import application


class Cut(Resource):

    def put(self, _id):
        context.application.data_manager.cut(_id)
        return application.make_ok_response()


class Copy(Resource):

    def put(self, _id):
        context.application.data_manager.copy(_id)
        return application.make_ok_response()


class Paste(Resource):

    def put(self, _id):
        context.application.data_manager.paste(_id)
        return application.make_ok_response()
