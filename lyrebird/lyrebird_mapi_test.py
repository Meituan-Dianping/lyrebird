import copy
import json
import binascii
import requests
base = "TQaGr3/VUFsO00A1TMYTaCx7CB77fIefk1ChL8DOXPbbcpnuLtjqV9W5OunqhutD3u8a2o4fXWfCk2h05kmoD0e+VdcCGTqNHAq9kFTnLnaivtUG/B2AXen455NnIHabHKN4jFU7cohoPgY5F+RgJUj8o2Vn9crd8r4pID+9iuKACEecCVKIjQj2b3Rc7uKo3iEwxZO5uYGJeI2aOjk0pwcSl1nKvlBvyqmNGNzSFt9yYGfCJy8MVc+jpzuX/dAib9lPDzLiOfs5kKPMUFPV7o0Zd5/QjZkXrS5B+VpmMVM="





env = 'prod'
resp_url = 'http://10.25.119.72:8080/mapi/resp'
req_url = 'http://10.25.119.72:8080/mapi/req'


bin_data = binascii.a2b_base64(base)
resp = requests.post(f'{resp_url}/decode', data=bin_data).text
json_data = json.loads(resp)
print(json_data)
encoded_mapi_body = requests.post(f'{resp_url}/encode', json=json_data)
b64_str = binascii.b2a_base64(encoded_mapi_body.content).decode()
print(b64_str)
# b64_str = binascii.b2a_base64(encoded_mapi_body.content).decode()
# print(encoded_mapi_body)
