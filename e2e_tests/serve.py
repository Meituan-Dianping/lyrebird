from flask import Flask, request
import hashlib

app = Flask(__name__)


@app.route("/e2e_serve", methods=["POST"])
def e2e_test():
    print('URL:', request.url)
    print('-------------------')
    print('Headers:', request.headers)
    req_body = request.get_data()
    if request.files and "file" in request.files:
        req_body = request.files['file'].read()
    return hashlib.md5(request.scheme.encode() + request.path.encode() + req_body).hexdigest()


if __name__ == "__main__":
    app.run()
