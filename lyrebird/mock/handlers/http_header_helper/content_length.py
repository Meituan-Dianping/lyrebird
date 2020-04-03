from ..http_data_helper import DataHelper


class ContentLengthHandler:

    @staticmethod
    def origin2flow(origin_obj):
        _resp_data = DataHelper.origin2flow(origin_obj)
        length = str(len(_resp_data))
        return length

    @staticmethod
    def flow2origin(flow_obj):
        _resp_data = DataHelper.flow2origin(flow_obj)
        length = str(len(_resp_data))
        return length
