from flask import jsonify
from . import cache
from .dm import DataManager, DataManagerV2
from .dm.file_data_adapter import data_adapter
from flask_socketio import SocketIO
from importlib import machinery
from pathlib import Path
import codecs
import json
import os
from lyrebird import application as app
from lyrebird.log import get_logger
import traceback
import time


"""
Mock server context

"""

logger = get_logger()


class DataManagerInitException(Exception):
    pass

class Mode:
    NORMAL = 'normal'
    RECORD = 'record'

    @staticmethod
    def contains(val):
        if val == Mode.NORMAL or val == Mode.RECORD:
            return True
        else:
            return False


class MockMode:
    NORMAL = 'normal'
    MULTIPLE = 'multiple'

    @staticmethod
    def contains(val):
        return val == MockMode.NORMAL or val == MockMode.MULTIPLE


class Application:

    def __init__(self):
        self._conf = None
        # todo 使用内存中的List存储请求，应可支持切换redis
        self.cache = cache.get_cache()
        self.work_mode = Mode.NORMAL
        self.is_diff_mode = MockMode.NORMAL
        self.filters = []
        self.selected_filter = {}
        self.data_manager = None
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

        self.init_datamanager()

        if _conf.get('mock.mode') == MockMode.MULTIPLE:
            self.is_diff_mode = MockMode.MULTIPLE

        if _conf.get('inspector.filters'):
            self.filters.extend(_conf.get('inspector.filters'))

        default_filter = _conf.get('inspector.default_filter')
        for f in self.filters:
            if f['name'] == default_filter:
                self.selected_filter = f
                break

    def init_datamanager(self):
        self._conf['datamanager.v2.enable'] = False
        data_versions = ['mock.data.v2', 'mock.data']
        for version in data_versions:
            uri = self._conf.get(version, 'data')
            if uri:
                adapter_cls = self._load_adapter(uri)
                if adapter_cls:
                    self.data_manager = self._get_data_manager(version)
                    self.data_manager.set_adapter(adapter_cls)
                    self.data_manager.set_root(uri)
                    return
        # If all versions fail, fallback to default file adapter
        logger.warning(f'Loading file data-adapter from {str(uri)} .')
        adapter_cls = data_adapter
        self.data_manager = DataManagerV2()
        self.data_manager.set_adapter(adapter_cls)
        self.data_manager.set_root(uri)
        return 

    def _load_adapter(self, uri):
        path = Path(uri).expanduser().absolute()
        if path.exists() and path.is_file():
            logger.warning(f'Loading custom data-adapter from {str(path)} .')
            try:
                loader = machinery.SourceFileLoader(path.stem, str(path))
                adapter_module = loader.load_module()
                return adapter_module.data_adapter
            except Exception:
                logger.error(f'Loading custom data-adapter from {str(path)} failed!\n{traceback.format_exc()}')
                raise DataManagerInitException

    def _get_data_manager(self, version):
        if version == 'mock.data.v2':
            self._conf['datamanager.v2.enable'] = True
            return DataManagerV2()
        else:
            return DataManager()

    def save(self):
        DEFAULT_CONF = os.path.join(
            os.path.join(os.path.expanduser('~'), '.lyrebird'), 'conf.json')
        # TODO Lyrebird 的 conf.json 应该有恢复机制或补救措施。
        with codecs.open(DEFAULT_CONF, 'w', 'utf-8') as f:
            f.write(json.dumps(self._conf, ensure_ascii=False, indent=4))

    def get_and_update_selected_filter_by_name(self, filter_name):
        old_filter = self.selected_filter
        if not filter_name:
            self.selected_filter = {}
        elif not old_filter or filter_name != old_filter['name']:
            for item in application.filters:
                if item['name'] == filter_name:
                    self.selected_filter = item
                    break
        app.config['inspector.default_filter'] = filter_name
        return self.selected_filter


"""
SocketIO emit interval
Because of iview table has render preformance problem
We need to limit render time
"""
EMIT_INTERVAL = 1
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


def emit(event, *args, **kwargs):
    now = time.time()
    last_push_time = last_emit_time.get(event, 0)
    if (now - last_push_time) > EMIT_INTERVAL:
        application.socket_io.emit(event, *args, **kwargs)
        last_emit_time[event] = now
