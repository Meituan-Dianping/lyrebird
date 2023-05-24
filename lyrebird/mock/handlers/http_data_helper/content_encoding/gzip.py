import gzip


class GzipHandler:

    @staticmethod
    def origin2flow(request_data):
        _data = gzip.decompress(request_data)
        return _data

    @staticmethod
    def flow2origin(flow_data):
        _data = gzip.compress(flow_data)
        return _data

    @staticmethod
    def origin2string(request_data):
        _data = gzip.decompress(request_data)
        return _data
