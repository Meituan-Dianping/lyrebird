class JavascriptHandler:

    @staticmethod
    def origin2flow(request_data):
        _data = request_data.decode('utf-8')
        return _data

    @staticmethod
    def flow2origin(flow_data):
        _data = flow_data.encode()
        return _data

    @staticmethod
    def origin2string(request_data):
        return request_data.decode('utf-8')
