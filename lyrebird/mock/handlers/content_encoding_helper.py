import gzip
from lyrebird.log import get_logger

logger = get_logger()


class ContentEncodingHelper:

    def __init__(self):
        self.content_encoding_map = {
            'gzip': {
                'origin2flow': self._gzip_origin2flow,
                'flow2origin': self._gzip_flow2origin
            }
        }

    def _gzip_origin2flow(self, request_data):
        _data = gzip.decompress(request_data)
        return _data

    def _gzip_flow2origin(self, flow_data):
        _data = gzip.compress(flow_data)
        return _data

    def _get_matched_action(self, content_encoding):
        if content_encoding in self.content_encoding_map:
            return self.content_encoding_map[content_encoding]

    def origin2flow(self, content_encoding, request_data):
        func = self._get_matched_action(content_encoding)
        _data = func['origin2flow'](request_data)
        return _data

    def flow2origin(self, content_encoding, flow_data):
        func = self._get_matched_action(content_encoding)
        _data = func['flow2origin'](flow_data)
        return _data
