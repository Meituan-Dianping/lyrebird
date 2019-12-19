from flask_restful import Resource
from lyrebird.mock import context
from flask import request
from ... import qrcode


class Qrcode(Resource):

    def post(self):
        link = request.json.get('link')
        qrcode_img = qrcode.get_qrcode_img(link)
        if qrcode_img:
            return context.make_ok_response(img=qrcode_img)
        else:
            return context.make_fail_response(f'make qrcode fail! Link is {link}')
