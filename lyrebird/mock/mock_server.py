from flask import Flask, redirect, url_for, request
from flask_cors import CORS
from . import context
from .blueprints.apis import api
from .blueprints.ui import ui
from .blueprints.core import core
from flask_socketio import SocketIO
from ..version import VERSION
from lyrebird.base_server import ThreadServer
from lyrebird import application
from lyrebird import log
import sys
import traceback

"""
Mock server

Lyrebird main server
Default port : 9090

* HTTP mock
* HTTP record
* Lyrebird UI
* Lyrebird API
* Lyrebird plugin management
"""

_logger = log.get_logger()


class LyrebirdMockServer(ThreadServer):
    """
    模拟接口服务
    使用flask在默认的9090端口启动,模拟线上接口,同时支持通过api动态修改接口数据。

    """

    def __init__(self):
        super().__init__()

        self.name = 'MockServer'
        self.conf = application.config
        # TODO rm conf rom mock context
        context.application.conf = application.config

        self.debug = False
        self.port = 9090
        self._working_thread = None
        self.app = self.create_app()
        # async_mode = threading / eventlet / gevent / gevent_uwsgi
        self.socket_io = SocketIO(self.app, async_mode='threading', logger=False, cors_allowed_origins='*')

        # 存储socket-io
        context.application.socket_io = self.socket_io
        application._socketio = self.socket_io

        # 生成过滤器实例
        if self.conf:
            self.port = self.conf.get('mock.port')
        else:
            _logger.error('Can not start mock server without config file')
            raise SyntaxError('Can not start mock server without config file.'
                              ' Default config file path = api-mock/conf.json')

        # Register blueprints
        self.app.register_blueprint(api)
        self.app.register_blueprint(core)
        self.app.register_blueprint(ui)

        @self.app.route('/')
        def index():
            """
            设置默认页面为UI首页
            """
            return redirect(url_for('ui.index')+f'?v={VERSION}')

        @self.app.errorhandler(Exception)
        def on_app_error(error):
            trace = traceback.format_exc()
            try:
                _logger.error(f'[mock server exception]: {trace}')
                _logger.error(f'[mock server exception]: {request.url}')
                _logger.error(f'[mock server exception]: {error}')
            except:
                # error handler must not raise any exceptions!
                pass

            return application.make_fail_response(f'Mock server error:\n {trace}')

    def create_app(self):
        app = Flask('MOCK')
        cors_resources = application.config.get('mock.server.cors.resources')
        if cors_resources and isinstance(cors_resources, dict):
            try:
                CORS(app, resources=cors_resources)
            except Exception as e:
                _logger.warning(f"An error occurred while setting CORS. The default mode does not support CORS. Error msg: {e}")
        return app

    def run(self):
        server_ip = application.config.get('ip')
        _logger.log(60, f'Core start on http://{server_ip}:{self.port}')
        if not sys.stdin or not sys.stdin.isatty():
            # For e2e testing start lyrebird in subprocess
            self.socket_io.run(self.app, host='0.0.0.0', port=self.port, debug=self.debug,
                               use_reloader=False, allow_unsafe_werkzeug=True)
        else:
            self.socket_io.run(self.app, host='0.0.0.0', port=self.port, debug=self.debug, use_reloader=False)

    def stop(self):
        """
        停止服务

        """
        super().stop()
    
    def terminate(self):
        super().terminate()
        try:
            self.socket_io.stop()
        except Exception as e:
            pass
        print('CoreServer shutdown')
