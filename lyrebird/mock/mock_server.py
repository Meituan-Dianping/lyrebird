import os
import sys
import time
import json
import errno
import socket
import datetime
import subprocess
from . import plugin_manager
from flask import Flask, request, redirect, url_for, Response, Blueprint, send_file
from . import context
from .blueprints.plugin import plugin
from .blueprints.apis import api
from .blueprints.ui import ui
from .blueprints.api_mock import api_mock
from flask_socketio import SocketIO
from .reporter import report_handler
from ..version import VERSION
from lyrebird.base_server import ThreadServer
from lyrebird import application
from lyrebird import log


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
    使用flask在默认的9090端口启动，模拟线上接口，同时支持通过api动态修改接口数据。

    """
    def __init__(self):
        super().__init__()
        
        self.conf = application.config
        # TODO rm conf rom mock context
        context.application.conf = application.config

        self.debug = False
        self.port = 9090
        self._working_thread = None
        self.app = Flask('MOCK')
        
        self.app.env = 'development'

        self.app.jinja_env.block_start_string = '[%'
        self.app.jinja_env.block_end_string = '%]'
        self.app.jinja_env.variable_start_string = '[['
        self.app.jinja_env.variable_end_string = ']]'
        self.app.jinja_env.comment_start_string = '[#'
        self.app.jinja_env.comment_end_string = '#]'

        # TODO delete
        # Add global function for templates
        # self.app.jinja_env.globals['time'] = time.time
        # self.app.jinja_env.globals['datetime'] = datetime.datetime
        # self.app.jinja_env.globals['version'] = VERSION

        # async_mode = threading / eventlet / gevent / gevent_uwsgi
        self.socket_io = SocketIO(self.app, async_mode='threading', logger=False)
        
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
        
        # Plugin
        # init plugin
        plugin_manager.load()
        # load plugin frontend
        plugin_manager.add_view_to_blueprint(ui)
        plugin_manager.add_view_to_blueprint(plugin)
        # Register event socket
        plugin_manager.add_event_rules(self.socket_io)
        # Register blueprints
        self.app.register_blueprint(api)
        self.app.register_blueprint(api_mock)
        self.app.register_blueprint(ui)
        self.app.register_blueprint(plugin)

        @self.app.route('/')
        def index():
            """
            设置默认页面为UI首页
            """
            return redirect(url_for('ui.index')+f'?v={VERSION}')

    def run(self):
        server_ip = application.config.get('ip')
        _logger.warning(f'start on http://{server_ip}:{self.port}')
        report_handler.start()
        self.socket_io.run(self.app, host='0.0.0.0', port=self.port, debug=self.debug, use_reloader=False)

    def stop(self):
        """
        停止服务

        """
        super().stop()
        try:
            self.socket_io.stop()
        except Exception:
            pass
        report_handler.stop()
        _logger.warning('MockServer shutdown')
