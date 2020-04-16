from lyrebird import on_request,on_request_upstream, on_response_upstream, on_response
from lyrebird import event

import requests
import binascii
import json
import copy

env = 'prod'
resp_url = 'http://10.25.119.72:8080/mapi/resp' if env == 'prod' else 'http://127.0.0.1:8080/mapi/resp'
req_url = 'http://10.25.119.72:8080/mapi/req'

# req 解密
@on_request(rules={
    "request.headers.User-Agent": "(?=.*MApi)",
    "request.headers.Pragma-Os": "(?=.*MApi)",
    "request.method": "POST",
})
def request_decode(ctx):
    print(ctx["request"]["data"])
    req_encrypted_data = ctx["request"]["data"]
    req_encrypted_bin_data = binascii.a2b_base64(req_encrypted_data)
    req_unencrypted_data = requests.post(f'{req_url}/decode', data=req_encrypted_bin_data).text
    print(req_unencrypted_data)
    ctx["request"]["data"] = req_unencrypted_data

# req 加密
@on_request_upstream(rules={
    "request.headers.User-Agent": "(?=.*MApi)",
    "request.headers.Pragma-Os": "(?=.*MApi)",
    "request.method": "POST",
})
def request_decode(ctx):
    req_unencrypted_data = ctx["request"]["data"]
    encrypted_data = requests.post(f'{req_url}/encode', data=req_unencrypted_data).content
    b64_str = binascii.b2a_base64(encrypted_data)
    ctx["request"]["data"] = b64_str


# resp 解密
@on_response_upstream(rules={
    "request.headers.User-Agent": "(?=.*MApi)",
    "request.headers.Pragma-Os": "(?=.*MApi)",
    "request.method": "POST",
})
def request_decode(ctx):
    print(ctx["request"]["url"])
    bin_data = binascii.a2b_base64(ctx["response"]["data"])
    resp = requests.post(f'{resp_url}/decode', data=bin_data)

    print(resp.text)
    













@on_response_upstream(rules={
    "request.headers.User-Agent": "(?=.*MApi)",
    "request.headers.Pragma-Os": "(?=.*MApi)",
    "request.method": "POST",
})
def resp_upstream(ctx):
    event.publish("mapi", ctx)

# # 解密
# # rules is_mapi
# @on_response_upstream(rules={
#     "request.headers.User-Agent": "(?=.*MApi)",
#     "request.headers.Pragma-Os": "(?=.*MApi)",
#     "request.url": "(?=.*http://mapi.dianping.com/general/platform/mttgdetail/mtmoredealslistgn.bin)"
# })
# def resp_upstream(ctx):


#     mapi_b64str = ctx["response"]["data"]


#     resp = requests.post(f'{base_url}/decode', data=binascii.a2b_base64(mapi_b64str)).text

#     try:
#         encoded_mapi_body = requests.post(f'{base_url}/encode', json=json.loads(resp)).content

#     except:
#         print(ctx["request"]["url"])
#         print("\n\n\n")
#         print(mapi_b64str)

#         print("\n\n\n\n")
#         print(resp)

#     a = binascii.b2a_base64(encoded_mapi_body).decode()

#     resp2 = requests.post(f'{base_url}/decode', data=binascii.a2b_base64(a)).text

#     print(resp == resp2)

#     ctx["response"]["data"] = a


# # # # 解密
# # @on_response(rules={
# #     "request.headers.User-Agent": "(?=.*MApi)",
# #     "request.headers.Pragma-Os": "(?=.*MApi)",
# #     # "request.url":"(?=.*http://mapi.dianping.com/general/platform/dztg/dznotice.bin)"
# # })
# # def resp(ctx):
# #     data = ctx["response"]["data"]
# # #     print(type(data))
# # #     encoded_mapi_body = requests.post(f'{base_url}/encode', json=data)
# # #     b64_str = binascii.b2a_base64(encoded_mapi_body.content).decode()

# # #     ctx["response"]["data"] = b64_str
