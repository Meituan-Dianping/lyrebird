from lyrebird import on_request,on_request_upstream, on_response_upstream, on_response
from lyrebird import event

import requests
import binascii
import json
import copy

env = 'prod'
resp_url = 'http://10.25.119.72:8080/mapi/resp' 
req_url = 'http://10.25.119.72:8080/mapi/req'

# req 解密
@on_request(rules={
    "request.headers.User-Agent": "(?=.*MApi)",
    "request.headers.Pragma-Os": "(?=.*MApi)",
    "request.method": "POST",
})
def request_decode(ctx):
    req_encrypted_data = ctx["request"]["data"]
    req_encrypted_bin_data = binascii.a2b_base64(req_encrypted_data)
    req_unencrypted_data = requests.post(f'{req_url}/decode', data=req_encrypted_bin_data).text
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
})
def response_decode(ctx):
    bin_data = binascii.a2b_base64(ctx["response"]["data"])
    resp = requests.post(f'{resp_url}/decode', data=bin_data).text
    try:
        json_data = json.loads(resp)
        ctx["response"]["data"] = resp
        ctx["response"]["headers"]["is_resp_decode"] = "1"
    except:
        ctx["response"]["headers"]["is_resp_decode"] = "0"

# resp 加密
@on_response(rules={
    "request.headers.User-Agent": "(?=.*MApi)",
    "request.headers.Pragma-Os": "(?=.*MApi)",
})
def response_encode(ctx):
    # send event
    mapi_cont = copy.deepcopy(ctx)
    # req
    if "data" in ctx["request"]:
        req_encrypted_data = ctx["request"]["data"]
        req_encrypted_bin_data = binascii.a2b_base64(req_encrypted_data)
        req_unencrypted_data = requests.post(f'{req_url}/decode', data=req_encrypted_bin_data).text
        mapi_cont["request"]["data"] = req_unencrypted_data
    event.publish("mapi", mapi_cont)

    if ctx["response"]["headers"]["is_resp_decode"] == "1":
        resp_unencrypted_data = ctx["response"]["data"]
        resp_unencrypted_json = json.loads(resp_unencrypted_data)
        encoded_mapi_body = requests.post(f'{resp_url}/encode', json=resp_unencrypted_json).content
        b64_str = binascii.b2a_base64(encoded_mapi_body).decode()
        ctx["response"]["data"] = b64_str

    


