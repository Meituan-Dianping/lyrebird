from urllib.parse import urlencode, parse_qs


class FormHandler:

    @staticmethod
    def origin2flow(request_data):
        _data = parse_qs(request_data.decode('utf-8'))
        return _data

    @staticmethod
    def flow2origin(flow_data):
        _data = urlencode(flow_data, doseq=True).encode()
        return _data
