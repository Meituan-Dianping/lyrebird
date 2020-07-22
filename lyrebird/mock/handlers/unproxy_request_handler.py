from flask import Response


class UnproxyRequest:

    def handle(self, handler_context):
        handler_context.is_proxiable = False

        headers = {
            'Content-Type': 'text/html; charset=utf-8'
        }
        code = 446
        resp_data = f'Lyrebird cannot proxy this request: {handler_context.flow.get("url")}\n'

        handler_context.response = Response(resp_data, status=code, headers=headers)
