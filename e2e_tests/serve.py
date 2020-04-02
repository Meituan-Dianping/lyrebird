from flask import Flask, request
import hashlib,json

app = Flask(__name__)


@app.route("/e2e_serve", methods=["POST"])
def e2e_test():

    req_body = request.get_data()
    if request.files and "file" in request.files:
        req_body = request.files['file'].read()
        return hashlib.md5(request.url.encode() + req_body).hexdigest()
    if "Content-Type" in request.headers and request.headers["Content-Type"] == "application/x-www-form-urlencoded":
        return hashlib.md5(request.url.encode() + json.dumps(request.form.to_dict()).encode()).hexdigest()
    return hashlib.md5(request.url.encode() + req_body).hexdigest()


if __name__ == "__main__":
    app.run()
