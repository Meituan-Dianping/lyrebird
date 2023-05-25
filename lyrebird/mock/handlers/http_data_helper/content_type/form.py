from urllib.parse import urlencode, parse_qs


class FormHandler:

    @staticmethod
    def origin2flow(request_data):
        params = parse_qs(request_data.decode('utf-8'), keep_blank_values=True)
        _data = {k:v[0] for k,v in params.items()}
        return _data

    @staticmethod
    def flow2origin(flow_data):
        _data = urlencode(flow_data).encode()
        return _data

    @staticmethod
    def origin2string(request_data):
        return request_data.decode('utf-8')
