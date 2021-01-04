from flask_restful import Resource
from lyrebird.mock import context
from flask import request
from lyrebird import application


class Notice(Resource):

    def get(self):
        return context.make_ok_response(
            noticeList=application.notice.notice_list,
            notRemindList=application.notice.not_remind_list
        )

    def put(self):
        notice_status = request.json.get('status')
        unique_key = request.json.get('key')
        application.notice.change_notice_status(unique_key, notice_status)
        return context.make_ok_response()

    def delete(self):
        unique_key = request.json.get('key')
        application.notice.delete_notice(unique_key)
        return context.make_ok_response()
