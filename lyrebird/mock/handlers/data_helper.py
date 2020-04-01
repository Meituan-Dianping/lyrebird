from .content_type_helper import ContentTypeHelper
from .content_encoding_helper import ContentEncodingHelper

content_type_helper = ContentTypeHelper()
content_encoding_helper = ContentEncodingHelper()

class RequestDataHelper:

    @staticmethod
    def req2flow(request, output=None):
        _data = request.data
        if not _data:
            return

        content_encoding = request.headers.get('Content-Encoding', '')
        if content_encoding:
            _data = content_encoding_helper.origin2flow(content_encoding, _data)

        content_type = request.headers.get('Content-Type', '')
        _data = content_type_helper.origin2flow(content_type, _data)

        if output:
            output['data'] = _data
        else:
            return _data

    @staticmethod
    def flow2req(flow, output=None):
        _data = flow['request'].get('data')
        if not _data:
            return

        content_type = flow['request']['headers'].get('Content-Type', '')
        _data = content_type_helper.flow2origin(content_type, _data)

        content_encoding = flow['request']['headers'].get('Content-Encoding', '')
        if content_encoding:
            content_type_helper.flow2origin(content_encoding, _data)

        if output:
            output.data = _data
        else:
            return _data

class ResponseDataHelper:

    @staticmethod
    def resp2flow(response, output=None):
        _data = response.data
        if not _data:
            return

        content_encoding = response.headers.get('Content-Encoding', '')
        if content_encoding:
            _data = content_encoding_helper.origin2flow(content_encoding, _data)

        content_type = response.headers.get('Content-Type', '')
        _data = content_type_helper.origin2flow(content_type, _data)

        if output:
            output['data'] = _data
        else:
            return _data

    @staticmethod
    def flow2resp(flow, output=None):
        _data = flow['response'].get('data')
        if not _data:
            return

        content_type = flow['response']['headers'].get('Content-Type', '')
        _data = content_type_helper.flow2origin(content_type, _data)

        content_encoding = flow['response']['headers'].get('Content-Encoding', '')
        if content_encoding:
            content_type_helper.flow2origin(content_encoding, _data)

        if output:
            output.data = _data
        else:
            return _data
