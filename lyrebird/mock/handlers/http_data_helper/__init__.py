from . import content_encoding, content_type


class DataHelper:

    @staticmethod
    def origin2flow(origin_obj, output=None):
        _data = origin_obj.data
        if not _data:
            return

        encoding_name = origin_obj.headers.get('Content-Encoding', '')
        _data = content_encoding.origin2flow(encoding_name, _data)

        type_name = origin_obj.headers.get('Content-Type', '')
        _data = content_type.origin2flow(type_name, _data)

        if output:
            output['data'] = _data
        else:
            return _data

    @staticmethod
    def flow2origin(flow_obj, output=None):
        _data = flow_obj.get('data')
        if not _data:
            return

        type_name = flow_obj['headers'].get('Content-Type', '')
        _data = content_type.flow2origin(type_name, _data)

        encoding_name = flow_obj['headers'].get('Content-Encoding', '')
        _data = content_encoding.flow2origin(encoding_name, _data)

        if output:
            output.data = _data
        else:
            return _data
