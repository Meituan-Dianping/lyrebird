from flask import Flask, request
import hashlib
import sys

app = Flask(__name__)


@app.route("/e2e_serve", methods=["POST"])
def e2e_test():

    req_body = request.get_data()
    if request.files and "file" in request.files:
        req_body = request.files['file'].read()
        return hashlib.md5(request.url.encode() + req_body).hexdigest()
    return hashlib.md5(request.url.encode() + req_body).hexdigest()


@app.route("/status", methods=["GET"])
def status():
    return "OK"


@app.route("/test_param/", methods=["GET"])
def test_param():
    param = request.args.get('param')
    return param


@app.route("/test_encoder_decoder/", methods=["POST"])
def test_encoder_decoder():
    return "OK"


if __name__ == "__main__":
    port = 5000
    if sys.argv:
        port = int(sys.argv[2])
    app.run(port=port)
