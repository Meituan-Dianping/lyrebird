from lyrebird.mock import context
from lyrebird.log import get_logger


logger = get_logger()


class MockHandler:
    """
    根据当前设置数据组的匹配条件,查找对应的mock数据。
    如果没有找到匹配的数据则交由下一个处理器处理。

    """

    def handle(self, handler_context):
        hit_datas = context.application.data_manager.get_matched_data(handler_context.flow)
        if len(hit_datas) <= 0:
            return

        # TODO 增加命中多条数据时的处理
        hit_data = hit_datas[0]

        activated_groups = context.application.data_manager.activated_group
        activated_group = list(activated_groups.values())[0]
        logger.info(
            f'<Mock> Hit Group:{activated_group.get("name")} - Data:{hit_data["name"]} \nURL: {handler_context.flow["request"]["url"]}\nGroupID:{activated_group["id"]} DataID:{hit_data["id"]}')

        handler_context.flow['response'] = hit_data['response']
        handler_context.flow['response']['headers']['isMocked'] = 'True'
        handler_context.flow['response']['headers']['lyrebird'] = 'mock'
        handler_context.set_response_state_json()
