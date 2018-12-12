from lyrebird.mock import context
from flask import Response


class MockHandler:
    """
    根据当前设置数据组的匹配条件,查找对应的mock数据。
    如果没有找到匹配的数据则交由下一个处理器处理。

    """
    def handle(self, handler_context):
        data = context.application.data_manager.router.get_mock_data(handler_context.flow)
        if data:
            handler_context.response = Response('OK: mock')
