from ..http_data_helper import DataHelper


class ContentLengthHandler:

    @staticmethod
    def origin2flow(origin_obj):
        _resp_data = DataHelper.origin2flow(origin_obj)
        if not _resp_data:
            return '0'
        return str(len(_resp_data))

    @staticmethod
    def flow2origin(flow_obj, chain=None):
        _resp_data = DataHelper.flow2origin(flow_obj, chain=chain)
        if not _resp_data:
            return '0'
        return str(len(_resp_data))
