from pathlib import Path
from lyrebird.mock import context
from lyrebird.log import get_logger
from .mock_data_helper import MockDataHelper


logger = get_logger()


class MockHandler:
    """
    根据当前设置数据组的匹配条件,查找对应的mock数据。

    """

    def handle(self, handler_context):
        hit_datas = context.application.data_manager.get_matched_data(handler_context.flow)
        if len(hit_datas) <= 0:
            return

        # TODO rules of hitting multiple mock data
        hit_data = hit_datas[0]

        activated_groups = context.application.data_manager.activated_group
        activated_group = list(activated_groups.values())[0]
        logger.info(
            f'<Mock> Hit Group:{activated_group.get("name")} - Data:{hit_data["name"]} \nURL: {handler_context.flow["request"]["url"]}\nGroupID:{activated_group["id"]} DataID:{hit_data["id"]}')

        handler_context.flow['response']['code'] = hit_data['response']['code']
        handler_context.flow['response']['headers'] = {k:v for k,v in hit_data['response']['headers'].items()}
        handler_context.flow['response']['data'] = hit_data['response']['data']

        handler_context.set_response_edited()
        handler_context.set_response_source_mock()
        handler_context.flow['response']['headers']['isMocked'] = 'True'
        handler_context.flow['response']['headers']['lyrebird'] = 'mock'
        handler_context.add_flow_action({
            'id': 'mock',
            'name': Path(__file__).name,
            'mock_id': hit_data['id']
        })
        MockDataHelper.read_mock_data(handler_context)
