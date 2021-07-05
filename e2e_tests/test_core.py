import pytest
from jinja2 import Template
import os, hashlib, json, gzip, requests


curPath = os.path.abspath(os.path.dirname(__file__))


serve_uri_template = "http://127.0.0.1:{{mock_server_port}}/e2e_serve"
mock_uri_template = "http://127.0.0.1:{{lyrebird_port}}/mock/"
uri_template = mock_uri_template + serve_uri_template


def _formate_uri(uri, mock_server_port=None, lyrebird_port=None):
    uri_template = Template(uri)
    return uri_template.render({
        'mock_server_port': mock_server_port,
        'lyrebird_port': lyrebird_port
    })

def test_img_data(lyrebird, mock_server):
    with open(f"{curPath}/assets/1.png", "rb") as f:
        data = f.read()
    uri = _formate_uri(uri_template, mock_server_port=mock_server.port, lyrebird_port=lyrebird.port)
    serve_uri = _formate_uri(serve_uri_template, mock_server_port=mock_server.port)
    r = requests.post(url=uri, data=data)
    assert r.text == hashlib.md5(serve_uri.encode() + data).hexdigest()

def test_img_file(lyrebird, mock_server):
    files = {'file': ('1.png', open(f'{curPath}/assets/1.png', 'rb'), 'image/jpg')}
    uri = _formate_uri(uri_template, mock_server_port=mock_server.port, lyrebird_port=lyrebird.port)
    serve_uri = _formate_uri(serve_uri_template, mock_server_port=mock_server.port)
    r = requests.post(uri, files=files)
    with open(f'{curPath}/assets/1.png', 'rb') as f:
        data = f.read()
    assert r.text == hashlib.md5(serve_uri.encode() + data).hexdigest()

def test_json(lyrebird, mock_server):
    data = json.dumps({"name": {"12": 123}}, ensure_ascii=False)
    headers = {"Content-Type": "application/json"}
    uri = _formate_uri(uri_template, mock_server_port=mock_server.port, lyrebird_port=lyrebird.port)
    serve_uri = _formate_uri(serve_uri_template, mock_server_port=mock_server.port)
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

def test_text(lyrebird, mock_server):
    data = "asdasdasd"
    headers = {"Content-Type": "text/plain"}
    uri = _formate_uri(uri_template, mock_server_port=mock_server.port, lyrebird_port=lyrebird.port)
    serve_uri = _formate_uri(serve_uri_template, mock_server_port=mock_server.port)
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

def test_form(lyrebird, mock_server):
    data = 'z=9&a=1&a=2&b=1'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    uri = _formate_uri(uri_template, mock_server_port=mock_server.port, lyrebird_port=lyrebird.port)
    serve_uri = _formate_uri(serve_uri_template, mock_server_port=mock_server.port)
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

def test_json_gzip(lyrebird, mock_server):
    data = {"a": 1}
    ziped_data = gzip.compress(json.dumps(data, ensure_ascii=False).encode())
    headers = {"Content-Type": "application/json", "Content-Encoding": "gzip"}
    uri = _formate_uri(uri_template, mock_server_port=mock_server.port, lyrebird_port=lyrebird.port)
    serve_uri = _formate_uri(serve_uri_template, mock_server_port=mock_server.port)
    r = requests.post(url=uri, data=ziped_data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + ziped_data).hexdigest()
