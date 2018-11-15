from lyrebird.mock import context
from flask import Response


class MockHandler:
    """
    根据当前设置数据组的匹配条件,查找对应的mock数据。
    如果没有找到匹配的数据则交由下一个处理器处理。

    """
    def handle(self, handler_context):
        group_id = context.application.data_manager.activated_group_id
        group = context.application.data_manager.groups.get(group_id)
        if not group:
            return
        data = group.router.get_mock_data(handler_context.flow)
        handler_context.response = Response(
            data.response_data.content, 
            200)

