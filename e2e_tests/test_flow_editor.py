import pytest
import os, hashlib, json, gzip, requests


curPath = os.path.abspath(os.path.dirname(__file__))


serve_uri = "http://127.0.0.1:5000/e2e_serve"
serve_status_uri = "http://127.0.0.1:5000/status"
api_uri = "http://127.0.0.1:9090/api/"
mock_uri = "http://127.0.0.1:9090/mock/"
uri = mock_uri + serve_uri


def test_flow_editor_img_data(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    with open(f"{curPath}/assets/1.png", "rb") as f:
        data = f.read()
    r = requests.post(url=uri, data=data, headers={'Content-Type': 'application/octet-stream'})
    assert r.text == hashlib.md5(serve_uri.encode() + data).hexdigest()

def test_flow_editor_img_file(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    files = {'file': ('1.png', open(f'{curPath}/assets/1.png', 'rb'), 'image/jpg')}
    r = requests.post(uri, files=files)
    with open(f'{curPath}/assets/1.png', 'rb') as f:
        data = f.read()
    assert r.text == hashlib.md5(serve_uri.encode() + data).hexdigest()

def test_flow_editor_json(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    data = json.dumps({"name": {"12": 123}}, ensure_ascii=False)
    headers = {"Content-Type": "application/json"}
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

def test_flow_editor_text(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    data = "asdasdasd"
    headers = {"Content-Type": "text/plain"}
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

def test_flow_editor_form(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    data = 'z=9&a=1&a=2&b=1'
    after_data = 'z=9&a=1&b=1'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + after_data.encode()).hexdigest()

def test_flow_editor_json_gzip(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path='./assets/flow_editor.py')
    data = {"a": 1}
    ziped_data = gzip.compress(json.dumps(data, ensure_ascii=False).encode())
    headers = {"Content-Type": "application/json", "Content-Encoding": "gzip"}
    r = requests.post(url=uri, data=ziped_data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + ziped_data).hexdigest()
