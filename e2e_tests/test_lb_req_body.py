import pytest
import time
import subprocess
import os, hashlib, json, gzip, requests


curPath = os.path.abspath(os.path.dirname(__file__))


serve_uri = "http://127.0.0.1:5000/e2e_serve"
serve_status_uri = "http://127.0.0.1:5000/status"
api_uri = "http://127.0.0.1:9090/api/"
mock_uri = "http://127.0.0.1:9090/mock/"
uri = mock_uri + serve_uri


def _wait(func, args=[], kwargs={}, timeout=15):
    count = 0
    while True:
        try:
            func(*args, **kwargs)
            return
        except Exception:
            count += 1
            time.sleep(1)
        if count > timeout:
            raise TimeoutError

@pytest.fixture
def lyrebird():
    print('start lyrebird server')
    test_server = subprocess.Popen('python3 serve.py', shell=True)
    _wait(requests.get, args=[serve_status_uri])
    lb = subprocess.Popen('lyrebird -b -v', shell=True)
    _wait(requests.get, args=[api_uri+'status'])
    yield 'lb'
    lb.kill()
    test_server.kill()
    print('stop lyrebird server')


def test_img_data(lyrebird):
    with open(f"{curPath}/1.png", "rb") as f:
        data = f.read()
    r = requests.post(url=uri, data=data)
    assert r.text == hashlib.md5(serve_uri.encode() + data).hexdigest()

def test_img_file(lyrebird):
    files = {'file': ('1.png', open(f'{curPath}/1.png', 'rb'), 'image/jpg')}
    r = requests.post(uri, files=files)
    with open(f'{curPath}/1.png', 'rb') as f:
        data = f.read()
    assert r.text == hashlib.md5(serve_uri.encode() + data).hexdigest()

def test_json(lyrebird):
    data = json.dumps({"name": {"12": 123}}, ensure_ascii=False)
    headers = {"Content-Type": "application/json"}
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

def test_text(lyrebird):
    data = "asdasdasd"
    headers = {"Content-Type": "text/plain"}
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

def test_form(lyrebird):
    data = 'z=9&a=1&a=2&b=1'
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(url=uri, data=data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

def test_json_gzip(lyrebird):
    data = {"a": 1}
    ziped_data = gzip.compress(json.dumps(data, ensure_ascii=False).encode())
    headers = {"Content-Type": "application/json", "Content-Encoding": "gzip"}
    r = requests.post(url=uri, data=ziped_data, headers=headers)
    assert r.text == hashlib.md5(serve_uri.encode() + ziped_data).hexdigest()

