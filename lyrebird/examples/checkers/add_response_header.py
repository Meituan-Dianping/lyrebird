from lyrebird import on_response
from lyrebird.checker import CheckerCategory

TITLE = '<示例脚本>在Response中添加Header Key'
CATEGORY = CheckerCategory.MODIFY

@on_response(rules={
    "request.url": "(?=.*poi/detail)"
})
def add_tag_in_response_headers(flow):
    flow['response']['headers']['Mock-Tag'] = 'Lyrebird'
