from lyrebird.mock import context
from lyrebird.log import get_logger
from flask import Response, stream_with_context


logger = get_logger()


class MockHandler:
    """
    根据当前设置数据组的匹配条件,查找对应的mock数据。
    如果没有找到匹配的数据则交由下一个处理器处理。

    """

    def handle(self, handler_context):
        data = context.application.data_manager.get_matched_data(handler_context.flow)
        if len(data) <= 0:
            return
        handler_context.response = self.data2response(data[0])
        activated_groups = context.application.data_manager.activated_group
        activated_group = list(activated_groups.values())[0]
        logger.info(
            f'<Mock> Hit Group:{activated_group.get("name")} - Data:{data[0]["name"]} \nURL: {handler_context.flow["request"]["url"]}\nGroupID:{activated_group["id"]} DataID:{data[0]["id"]}')

    def data2response(self, data):
        response = data['response']
        code = response['code']
        headers = response['headers']
        headers['lyrebird'] = 'mock'
        resp_data = response['data']

        if resp_data:
            if type(resp_data) == str:
                data_len = len(resp_data.encode())
            else:
                data_len = len(resp_data)
            headers['Content-Length'] = data_len
        else:
            # Handle none response data
            resp_data = ''

        def gen():
            yield resp_data
        return Response(stream_with_context(gen()), status=code, headers=headers)
