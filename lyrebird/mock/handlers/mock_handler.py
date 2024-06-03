from pathlib import Path
from lyrebird import utils
from lyrebird.mock.dm.jsonpath import jsonpath
from lyrebird.mock import context
from lyrebird.log import get_logger
from .mock_data_helper import MockDataHelper
from lyrebird.application import config
from lyrebird.config import CONFIG_MOCK_REQUEST_SSR_MOCK_IN_BODY, CONFIG_MOCK_REQUEST_SSR_MOCK_IN_BODY_PARAM, CONFIG_MOCK_REQUEST_SSR_MOCK_BODY_KEY, CONFIG_MOCK_REQUEST_SSR_MOCK_DATA_JSONPATH


logger = get_logger()


class MockHandler:
    """
    根据当前设置数据组的匹配条件,查找对应的mock数据。

    """

    @staticmethod
    def is_handle_ssr(handler_context):
        if not config.get(CONFIG_MOCK_REQUEST_SSR_MOCK_IN_BODY):
            return False

        key = config.get(CONFIG_MOCK_REQUEST_SSR_MOCK_IN_BODY_PARAM, 'is_ssr')
        is_open_ssr = handler_context.flow['request']['query'].get(key)
        if not is_open_ssr:
            return False

        if 'data' in handler_context.flow['request'] and not isinstance(handler_context.flow['request']['data'], dict):
            logger.warning('ssr but request body type is not Object')
            return False

        return True

    def handle(self, handler_context):
        hit_datas_info = context.application.data_manager.get_matched_data_multiple_source(handler_context.flow)
        if not hit_datas_info:
            return

        hit_datas = hit_datas_info['data']
        if len(hit_datas) <= 0:
            return

        # TODO rules of hitting multiple mock data
        hit_data = hit_datas[0]
        activated_group = hit_datas_info['parent']

        is_ssr = MockHandler.is_handle_ssr(handler_context)
        if is_ssr:
            logger.info(
                f'<Mock> <SSR> Hit Group:{activated_group.get("name")} - Data:{hit_data["name"]} \nURL: {handler_context.flow["request"]["url"]}\nGroupID:{activated_group["id"]} DataID:{hit_data["id"]}')

            request_data_update = {}

            resp_key = config.get(CONFIG_MOCK_REQUEST_SSR_MOCK_BODY_KEY, 'lyrebird_mock_response')
            request_data_update[resp_key] = hit_data['response'].get('data', '')

            resp_jsonpath = config.get(CONFIG_MOCK_REQUEST_SSR_MOCK_DATA_JSONPATH)
            if resp_jsonpath:
                request_data_update[resp_key] = utils.flow_str_2_data(request_data_update[resp_key])
                target_response_data = jsonpath.search(request_data_update[resp_key], resp_jsonpath, find_one=True)
                request_data_update[resp_key] = utils.flow_data_2_str(target_response_data)

            if 'data' not in handler_context.flow['request']:
                handler_context.flow['request']['data'] = {}
            handler_context.flow['request']['data'].update(request_data_update)

            handler_context.set_request_edited()
            handler_context.flow['request']['headers']['lyrebird'] = 'mock'

            handler_context.add_flow_action({
                'id': 'mock_ssr',
                'name': Path(__file__).name,
                'group_id': activated_group['id'],
                'mock_id': hit_data['id']
            })
            handler_context.flow['apiDiffConfig'] = hit_data.get('apiDiffConfig')
            return

        logger.info(
            f'<Mock> Hit Group:{activated_group.get("name")} - Data:{hit_data["name"]} \nURL: {handler_context.flow["request"]["url"]}\nGroupID:{activated_group["id"]} DataID:{hit_data["id"]}')
        handler_context.flow['response']['code'] = hit_data['response']['code']
        handler_context.flow['response']['headers'] = {k:v for k,v in hit_data['response']['headers'].items()}
        handler_context.flow['response']['data'] = hit_data['response'].get('data', '')

        handler_context.set_response_edited()
        handler_context.set_response_source_mock()
        handler_context.flow['response']['headers']['isMocked'] = 'True'
        handler_context.flow['response']['headers']['lyrebird'] = 'mock'
        handler_context.add_flow_action({
            'id': 'mock',
            'name': Path(__file__).name,
            'group_id': activated_group['id'],
            'mock_id': hit_data['id']
        })
        handler_context.flow['apiDiffConfig'] = hit_data.get('apiDiffConfig')
        MockDataHelper.read_mock_data(handler_context)
