import binascii


class DefaultHandler:

    @staticmethod
    def origin2flow(request_data):
        _data = binascii.b2a_base64(request_data).decode('utf-8')
        return _data

    @staticmethod
    def flow2origin(flow_data):
        _data = binascii.a2b_base64(flow_data)
        return _data

    @staticmethod
    def origin2string(request_data):
        _data = binascii.b2a_base64(request_data).decode('utf-8')
        return _data
