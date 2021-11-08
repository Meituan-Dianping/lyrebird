from lyrebird import on_request
from lyrebird.checker import CheckerCatetory

TITLE = '<示例脚本>在Request中添加Param'
CATEGORY = CheckerCatetory.MODIFY

@on_request(rules={
    "request.url": "(?=.*poi/detail)"
})
def add_request_param(flow):
    if '?' in flow['request']['url']:
        flow['request']['url'] += '&param=1'
    else:
        flow['request']['url'] += '?param=1'


