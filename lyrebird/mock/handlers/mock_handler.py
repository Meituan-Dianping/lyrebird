from lyrebird.mock import context


class MockHandler:
    """
    根据当前设置数据组的匹配条件,查找对应的mock数据。
    如果没有找到匹配的数据则交由下一个处理器处理。

    """
    def handle(self, handler_context):
        pass
        # data_group = context.application.data_manager.current_data_group
        # if data_group:
        #     handler_context.response = data_group.get_response(handler_context.get_origin_url(),
        #                                                        handler_context.request.data)
