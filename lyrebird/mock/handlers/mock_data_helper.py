import json
from lyrebird.log import get_logger

logger = get_logger()

class MockDataHelper:

    @staticmethod
    def read_mock_data(handler_context):
        content_type = handler_context.flow['response']['headers'].get('Content-Type', '')

        try:
            if content_type.startswith('application/json'):
                handler_context.flow['response']['data'] = json.loads(handler_context.flow['response']['data'])
            elif content_type.startswith('application/x-www-form-urlencoded'):
                handler_context.flow['response']['data'] = json.loads(handler_context.flow['response']['data'])

        except Exception as e:
            logger.warning(f'Convert mock data response failed. {e}')
