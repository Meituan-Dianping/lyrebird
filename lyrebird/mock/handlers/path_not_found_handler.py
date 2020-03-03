from flask import abort


class RequestPathNotFound:

    def handle(self, handler_context):
        return abort(404, 'Request path not found\n')
