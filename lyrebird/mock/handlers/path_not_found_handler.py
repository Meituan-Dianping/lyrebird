from flask import Response


class RequestPathNotFound:

    def handle(self, handler_context):
        headers = {
            'Content-Type': 'text/html; charset=utf-8'
        }
        code = 404
        resp_data = 'Request path not found\n'

        handler_context.flow['response']['headers'] = headers
        handler_context.flow['response']['code'] = code
        handler_context.flow['response']['data'] = resp_data

        handler_context.response = Response(resp_data, status=code, headers=headers)
