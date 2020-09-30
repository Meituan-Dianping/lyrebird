from flask_restful import Resource
from lyrebird.mock import context
from flask import request
from ... import qrcode

LINK_MAX_LENGTH = 2048


class Qrcode(Resource):

    def post(self):
        link = request.json.get('link', '')
        link_length = len(link)
        if link_length > LINK_MAX_LENGTH:
            return context.make_fail_response(f'Current length {link_length} overflows, expected length is less than {LINK_MAX_LENGTH}')
        qrcode_img = qrcode.get_qrcode_img(link)
        if qrcode_img:
            return context.make_ok_response(img=qrcode_img)
        else:
            return context.make_fail_response(f'make qrcode fail! Link is {link}')
