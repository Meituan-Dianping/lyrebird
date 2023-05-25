import json


class JsonHandler:

    @staticmethod
    def origin2flow(request_data):
        _data = json.loads(request_data.decode('utf-8'))
        return _data

    @staticmethod
    def flow2origin(flow_data):
        _data = json.dumps(flow_data, ensure_ascii=False).encode()
        return _data

    @staticmethod
    def origin2string(request_data):
        return request_data.decode('utf-8')
