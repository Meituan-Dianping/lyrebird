from lyrebird.mock import context
from lyrebird.log import get_logger


logger = get_logger()


class MockHandler:
    """
    根据当前设置数据组的匹配条件,查找对应的mock数据。
    如果没有找到匹配的数据则交由下一个处理器处理。

    """

    def handle(self, handler_context):
        handler_context.update_server_req_time()

        hit_datas = context.application.data_manager.get_matched_data(handler_context.flow)
        if len(hit_datas) <= 0:
            return

        hit_data = hit_datas[0]
        content_type = hit_data['response']['headers'].get('Content-Type')
        content_type = content_type.strip()
        if not content_type:
            pass
        elif content_type.startswith('application/json'):
            pass
        elif content_type.startswith('text/xml'):
            hit_data['response']['data'] = hit_data['response']['data'].encode()
        elif content_type.startswith('text/html'):
            hit_data['response']['data'] = hit_data['response']['data'].encode()
        else:
            # TODO write bin data
            hit_data['response']['data'] = hit_data['response']['data'].encode()

        activated_groups = context.application.data_manager.activated_group
        activated_group = list(activated_groups.values())[0]
        logger.info(
            f'<Mock> Hit Group:{activated_group.get("name")} - Data:{hit_data["name"]} \nURL: {handler_context.flow["request"]["url"]}\nGroupID:{activated_group["id"]} DataID:{hit_data["id"]}')

        handler_context.update_server_resp_time()
        return hit_data
