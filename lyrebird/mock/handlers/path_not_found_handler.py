from flask import Response


class RequestPathNotFound:

    def handle(self, handler_context):
        handler_context.flow['response']['code'] = 404
        return Response('Request path not found\n', 404)
