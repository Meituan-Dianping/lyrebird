import json
import multiprocessing
import os
import socket
from contextlib import closing
from urllib import parse

import eventlet
import requests
from eventlet import wsgi
from flask import Flask, Response, app, request, stream_with_context
from lyrebird import application
from lyrebird.base_server import ThreadServer
from lyrebird.log import get_logger

logger = get_logger()
lb_conf = None

os.environ['EVENTLET_HUB'] = 'poll'


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD'])
def index(path=None):
    logger.info(f'<ExtraMock> On request {request.url}')
    # Read origin headers
    raw_headers = list(request.environ['headers_raw'])
    # update url
    origin_url = request.url
    parsed_url = parse.urlparse(origin_url)
    modified_url = parsed_url._replace(netloc=f'localhost:{lb_conf.get("mock.port")}', path='/mock'+parsed_url.path)
    url = modified_url.geturl()
    # Data
    data = request.data or request.form or None
    # Porxy request to core server
    res = requests.request(request.method, url, headers={'Proxy-Raw-Headers':json.dumps(dict(raw_headers))}, data=data, stream=True, verify=False, allow_redirects=False)

    headers = {}
    for name,value in res.headers.items():
        headers[name] = value
    return Response(stream_with_context(res.iter_content(chunk_size=1024)), status=res.status_code, headers=headers)


def eventlet_server(conf=None):
    global lb_conf
    lb_conf = conf

    # Default extra mock port is 9999
    port = lb_conf.get('extra.mock.port') if lb_conf.get('extra.mock.port') else 9999

    logger.info(f'ExtraMockServer start on {port}')
    wsgi.server(eventlet.listen(('', port)), app.wsgi_app)


class ExtraMockServer():
    def __init__(self) -> None:
        self._server_process = None

    def start(self):
        self._server_process = multiprocessing.Process(group=None, target=eventlet_server, kwargs={'conf': application.config.raw()})
        self._server_process.start()

    def stop(self):
        if self._server_process:
            self._server_process.terminate()
            logger.warning(f'MockServer shutdown')
            self._server_process = None
