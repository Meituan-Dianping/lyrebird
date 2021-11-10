from flask import Response
from lyrebird.mock import lb_http_status
from lyrebird.log import get_logger


logger = get_logger()

class RequestKilled:

    def handle(self, handler_context):
        url = ''
        if 'url' in handler_context.flow.get('request'):
            url = handler_context.flow['request']['url']

        headers = {
            'Lyrebird-Mitmproxy-Command': 'kill'
        }
        code = 0
        resp_data = ''

        handler_context.flow['response']['headers'] = {}
        handler_context.flow['response']['code'] = 0
        handler_context.flow['response']['data'] = ''

        handler_context.response = Response(resp_data, status=code, headers=headers)
        logger.info(f'<Proxy> ERROR::CAN_NOT_HANDLE_REQUEST {url}')
