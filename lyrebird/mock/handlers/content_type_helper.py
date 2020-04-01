import json
import binascii
from urllib.parse import urlencode, parse_qs
from collections import OrderedDict
from lyrebird.log import get_logger

logger = get_logger()


class ContentTypeHelper:

    def __init__(self):
        self.content_type_map = OrderedDict({
            'application/x-www-form-urlencoded': {
                'origin2flow': self._form_origin2flow,
                'flow2origin': self._form_flow2origin
            },
            'application/json': {
                'origin2flow': self._json_origin2flow,
                'flow2origin': self._json_flow2origin
            },
            'text/': {
                'origin2flow': self._text_origin2flow,
                'flow2origin': self._text_flow2origin
            },
            '': {
                'origin2flow': self._unknown_origin2flow,
                'flow2origin': self._unknown_flow2origin
            }
        })

    def _form_origin2flow(self, request_data):
        return parse_qs(request_data.decode('utf-8'))

    def _form_flow2origin(self, flow_data):
        return urlencode(flow_data).encode()

    def _json_origin2flow(self, request_data):
        return json.loads(request_data.decode('utf-8'))

    def _json_flow2origin(self, flow_data):
        return json.dumps(flow_data).encode()

    def _text_origin2flow(self, request_data):
        return request_data.decode('utf-8')

    def _text_flow2origin(self, flow_data):
        return flow_data.encode()

    def _unknown_origin2flow(self, request_data):
        return binascii.b2a_base64(request_data).decode('utf-8')

    def _unknown_flow2origin(self, flow_data):
        return binascii.a2b_base64(flow_data)

    def _get_matched_action(self, content_type):
        for pattern, func in self.content_type_map.items():
            if content_type.startswith(pattern):
                return func
        return self.content_type_map['']

    def origin2flow(self, content_type, request_data):
        func = self._get_matched_action(content_type)
        _data = func['origin2flow'](request_data)
        return _data

    def flow2origin(self, content_type, flow_data):
        func = self._get_matched_action(content_type)
        _data = func['flow2origin'](flow_data)
        return _data
