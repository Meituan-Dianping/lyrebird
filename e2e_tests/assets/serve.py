from flask import Flask, request
import hashlib

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

if __name__ == "__main__":
    app.run()
