import os, sys, time, hashlib, base64, json, gzip, requests,urllib
from urllib import parse


curPath = os.path.abspath(os.path.dirname(__file__))


def setup_module():
    os.system("nohup python3 serve.py > /dev/null 2>&1 & ")
    os.system("nohup lyrebird -b > /dev/null 2>&1 & ")
    print("init serve")
    time.sleep(3)


def teardown_module():
    os.system(
        "ps -ef|grep serve.py | grep -v grep|awk '{printf $2}'|xargs kill -9"
    )
    os.system(
        "ps -ef|grep lyrebird | grep -v grep|awk '{printf $2}'|xargs kill -9"
    )
    print("teardown")


serve_uri = "http://127.0.0.1:5000/e2e_serve"
mock_uri = "http://127.0.0.1:9090/mock/"
uri = mock_uri + serve_uri


class TestSuite:
    def test_img_data(self):
        with open(f"{curPath}/1.png", "rb") as f:
            data = f.read()
        r = requests.post(url=uri, data=data)
        assert r.text == hashlib.md5(serve_uri.encode() + data).hexdigest()

    def test_img_file(self):
        files = {'file': ('1.png', open(f'{curPath}/1.png', 'rb'), 'image/jpg')}
        r = requests.post(uri, files=files)
        with open(f'{curPath}/1.png', 'rb') as f:
            data = f.read()
        assert r.text == hashlib.md5(serve_uri.encode() + data).hexdigest()
    
    def test_json(self):
        data = json.dumps({"name": {"12": 123}})
        headers = {"Content-Type": "application/json"}
        r = requests.post(url=uri, data=data, headers=headers)
        assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

    def test_text(self):
        data = "asdasdasd"
        headers = {"Content-Type": "text/plain"}
        r = requests.post(url=uri, data=data, headers=headers)
        assert r.text == hashlib.md5(serve_uri.encode() + data.encode()).hexdigest()

    def test_form(self):
        data = {"a": 1, "b": 2}
        dict2params = urllib.parse.parse_qs(urllib.parse.urlencode(data))
        params2json = json.dumps({key: dict2params[key][0] for key in dict2params})
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r = requests.post(url=uri, data=data, headers=headers)
        assert r.text == hashlib.md5(serve_uri.encode() + params2json.encode()).hexdigest()

    def test_json_gzip(self):
        data = {"a": 1}
        ziped_data = gzip.compress(json.dumps(data).encode())
        headers = {"Content-Type": "application/json", "Content-Encoding": "gzip"}
        r = requests.post(url=uri, data=ziped_data, headers=headers)
        assert r.text == hashlib.md5(serve_uri.encode() + ziped_data).hexdigest()

