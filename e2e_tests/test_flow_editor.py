import time
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


def test_flow_editor_img_data(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    # Wait for checker to load
    time.sleep(3)

    with open(f"{curPath}/assets/1.png", "rb") as f:
        data = f.read()
    uri = _formate_uri(uri_template, mock_server_port=mock_server.port, lyrebird_port=lyrebird_with_args.port)
    serve_uri = _formate_uri(serve_uri_template, mock_server_port=mock_server.port)
    r = requests.post(url=uri, data=data, headers={'Content-Type': 'application/octet-stream'})
    assert r.text == hashlib.md5(serve_uri.encode() + data).hexdigest()

def test_flow_editor_img_file(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    # Wait for checker to load
    time.sleep(3)

    files = {'file': ('1.png', open(f'{curPath}/assets/1.png', 'rb'), 'image/jpg')}
    uri = _formate_uri(uri_template, mock_server_port=mock_server.port, lyrebird_port=lyrebird_with_args.port)
    serve_uri = _formate_uri(serve_uri_template, mock_server_port=mock_server.port)
    r = requests.post(uri, files=files)
    with open(f'{curPath}/assets/1.png', 'rb') as f:
        data = f.read()
    assert r.text == hashlib.md5(serve_uri.encode() + data).hexdigest()

def test_flow_editor_json(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    # Wait for checker to load
    time.sleep(3)

    data = json.dumps({"name": {"12": 123}}, ensure_ascii=False)
    headers = {"Content-Type": "application/json"}
    uri = _formate_uri(uri_template, mock_server_port=mock_server.port, lyrebird_port=lyrebird_with_args.port)
    serve_uri = _formate_uri(serve_uri_template, mock_server_port=mock_server.port)
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

def test_empty_case(lyrebird_with_args, mock_server):
    pass

def test_flow_editor_text(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    # Wait for checker to load
    time.sleep(3)

    data = "asdasdasd"
    headers = {"Content-Type": "text/plain"}
    uri = _formate_uri(uri_template, mock_server_port=mock_server.port, lyrebird_port=lyrebird_with_args.port)
    serve_uri = _formate_uri(serve_uri_template, mock_server_port=mock_server.port)
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

def test_flow_editor_form(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    # Wait for checker to load
    time.sleep(3)

    data = 'z=9&a=1&a=2&b=1'
    after_data = 'z=9&a=1&b=1'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    uri = _formate_uri(uri_template, mock_server_port=mock_server.port, lyrebird_port=lyrebird_with_args.port)
    serve_uri = _formate_uri(serve_uri_template, mock_server_port=mock_server.port)
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + after_data.encode()).hexdigest()

def test_flow_editor_json_gzip(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    # Wait for checker to load
    time.sleep(3)

    data = {"a": 1}
    ziped_data = gzip.compress(json.dumps(data, ensure_ascii=False).encode())
    headers = {"Content-Type": "application/json", "Content-Encoding": "gzip"}
    uri = f'http://127.0.0.1:{lyrebird_with_args.port}/mock/http://127.0.0.1:{mock_server.port}/e2e_serve'
    serve_uri = f'http://127.0.0.1:{mock_server.port}/e2e_serve'
    r = requests.post(url=uri, data=ziped_data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + ziped_data).hexdigest()
