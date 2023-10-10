from flask import Flask, request
import hashlib
import sys
import time

app = Flask(__name__)
CORE_TIME = 0.6


@app.route("/e2e_serve", methods=["POST"])
def e2e_test():

    req_body = request.get_data()
    if request.files and "file" in request.files:
        req_body = request.files["file"].read()
        return hashlib.md5(request.url.encode() + req_body).hexdigest()
    return hashlib.md5(request.url.encode() + req_body).hexdigest()


@app.route("/status", methods=["GET"])
def status():
    return "OK"


@app.route("/performance", methods=["GET"])
def performance():
    time.sleep(CORE_TIME)
    return "OK"


if __name__ == "__main__":
    port = 5000
    if sys.argv:
        port = int(sys.argv[2])
    app.run(port=port)
