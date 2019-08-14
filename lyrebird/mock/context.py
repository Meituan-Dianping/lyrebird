from flask import jsonify, stream_with_context, Response
from . import cache
from .filesystem import FileManager
from .data_manager import DataManager
from flask_socketio import SocketIO
import codecs, json, os
from lyrebird import application as app
import time


"""
Mock server context

"""

class Mode:
    NORMAL = 'normal'
    RECORD = 'record'

    @staticmethod
    def contains(val):
        if val==Mode.NORMAL or val==Mode.RECORD:
            return True
        else:
            return False 

class Application:

    def __init__(self):
        self._conf = None
        # todo 使用内存中的List存储请求，应可支持切换redis
        self.cache = cache.get_cache()
        self.work_mode = Mode.NORMAL
        # todo 使用文件系统存储mock数据，应可支持切换redis，mysql
        # self.data_manager = FileManager()
        self.data_manager = DataManager()
        # SocketIO
        self.socket_io: SocketIO = None
        self.conf_manager = None
        self.current_conf_name = None

    @property
    def event_bus(self):
        return app.server.get('event')

    @property
    def conf(self):
        return self._conf

    @conf.setter
    def conf(self, _conf):
        self._conf = _conf
        # TODO 更新conf触发更新data_manager根目录
        if _conf.get('mock.data'):
            self.data_manager.root = _conf.get('mock.data')

    def save(self):
        DEFAULT_CONF = os.path.join(
            os.path.join(os.path.expanduser('~'), '.lyrebird'), 'conf.json')
        # TODO Lyrebird 的 conf.json 应该有恢复机制或补救措施。
        with codecs.open(DEFAULT_CONF, 'w', 'utf-8') as f:
            f.write(json.dumps(self._conf, ensure_ascii=False, indent=4))


"""
SocketIO emit interval
Because of iview table has render preformance problem
We need to limit render time
"""
EMIT_INTERVAL = 0.4
last_emit_time = {}


application = Application()


def make_ok_response(**kwargs):
    ok_resp = {
            "code": 1000,
            "message": "success"
        }
    ok_resp.update(kwargs)
    return jsonify(ok_resp)


def make_fail_response(msg, code=3000, **kwargs):
    fail_resp = {
            "code": code,
            "message": msg
        }
    fail_resp.update(kwargs)
    return jsonify(fail_resp)


def make_streamed_response(generator, code=200, mimetype='application/json'):
    return Response(stream_with_context(generator()), mimetype=mimetype, status=code)


def emit(event, *args, **kwargs):
    now = time.time()
    last_push_time = last_emit_time.get(event, 0)
    if (now - last_push_time) > EMIT_INTERVAL:
        application.socket_io.emit(event, *args, **kwargs)
        last_emit_time[event] = now
