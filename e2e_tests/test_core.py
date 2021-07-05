import pytest
import os, hashlib, json, gzip, requests


curPath = os.path.abspath(os.path.dirname(__file__))


def test_img_data(lyrebird, mock_server):
    with open(f"{curPath}/assets/1.png", "rb") as f:
        data = f.read()
    r = requests.post(url=lyrebird.uri_mock + mock_server.api_post, data=data)
    assert r.text == hashlib.md5(mock_server.api_post.encode() + data).hexdigest()

def test_img_file(lyrebird, mock_server):
    files = {'file': ('1.png', open(f'{curPath}/assets/1.png', 'rb'), 'image/jpg')}
    r = requests.post(url=lyrebird.uri_mock + mock_server.api_post, files=files)
    with open(f'{curPath}/assets/1.png', 'rb') as f:
        data = f.read()
    assert r.text == hashlib.md5(mock_server.api_post.encode() + data).hexdigest()

def test_json(lyrebird, mock_server):
    data = json.dumps({"name": {"12": 123}}, ensure_ascii=False)
    headers = {"Content-Type": "application/json"}
    r = requests.post(url=lyrebird.uri_mock + mock_server.api_post, data=data, headers=headers)
    assert r.text == hashlib.md5(mock_server.api_post.encode() + data.encode()).hexdigest()

def test_text(lyrebird, mock_server):
    data = "asdasdasd"
    headers = {"Content-Type": "text/plain"}
    r = requests.post(url=lyrebird.uri_mock + mock_server.api_post, data=data, headers=headers)
    assert r.text == hashlib.md5(mock_server.api_post.encode() + data.encode()).hexdigest()

def test_form(lyrebird, mock_server):
    data = 'z=9&a=1&a=2&b=1'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(url=lyrebird.uri_mock + mock_server.api_post, data=data, headers=headers)
    assert r.text == hashlib.md5(mock_server.api_post.encode() + data.encode()).hexdigest()

def test_json_gzip(lyrebird, mock_server):
    data = {"a": 1}
    ziped_data = gzip.compress(json.dumps(data, ensure_ascii=False).encode())
    headers = {"Content-Type": "application/json", "Content-Encoding": "gzip"}
    r = requests.post(url=lyrebird.uri_mock + mock_server.api_post, data=ziped_data, headers=headers)
    assert r.text == hashlib.md5(mock_server.api_post.encode() + ziped_data).hexdigest()
