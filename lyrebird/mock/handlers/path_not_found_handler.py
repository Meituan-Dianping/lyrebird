from flask import Response


class RequestPathNotFound:

    def handle(self, handler_context):
        if not handler_context.response:
            handler_context.response = Response('Request path not found\n', 404)
