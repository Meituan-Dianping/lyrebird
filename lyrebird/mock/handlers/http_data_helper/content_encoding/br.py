import brotli


class BrotliHandler:

    @staticmethod
    def origin2flow(request_data):
        _data = brotli.decompress(request_data)
        return _data

    @staticmethod
    def flow2origin(flow_data):
        _data = brotli.compress(flow_data)
        return _data

    @staticmethod
    def origin2string(request_data):
        _data = brotli.decompress(request_data)
        return _data
