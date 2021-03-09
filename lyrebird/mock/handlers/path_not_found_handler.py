from flask import Response
from lyrebird.mock import lb_http_status
from lyrebird.log import get_logger


logger = get_logger()

class RequestPathNotFound:

    def handle(self, handler_context):
        url = ''
        if 'url' in handler_context.flow.get('request'):
            url = handler_context.flow['request']['url']

        headers = {
            'Content-Type': 'text/html; charset=utf-8'
        }
        code = lb_http_status.STATUS_CODE_CAN_NOT_HANDLE_REQUEST
        resp_data = f'Lyrebird cannot handle this request: {url}\n'

        handler_context.flow['response']['headers'] = headers
        handler_context.flow['response']['code'] = code
        handler_context.flow['response']['data'] = resp_data

        handler_context.response = Response(resp_data, status=code, headers=headers)
        logger.info(f'<Proxy> ERROR::CAN_NOT_HANDLE_REQUEST {url}')
