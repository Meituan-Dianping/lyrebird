from lyrebird import on_response

@on_response(rules={
    "request.url": "(?=.*poi/detail)"
})
def add_tag_in_response_headers(flow):
    flow['response']['headers']['Mock-Tag'] = 'Lyrebird'
