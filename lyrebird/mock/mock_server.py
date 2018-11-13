import os
import sys
import json
import errno
import socket
import datetime
import subprocess
from . import plugin_manager
from flask import Flask, request, redirect, url_for, Response
from . import context
from .blueprints.api import api
from .blueprints.ui import ui
from .blueprints.api_mock import api_mock
from flask_socketio import SocketIO
from .reporter import report_handler
from ..version import VERSION
from lyrebird.base_server import ThreadServer
from lyrebird import application
from lyrebird import log
from flask_sqlalchemy import SQLAlchemy
from lyrebird.mock.db.database import DataBase


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

current_dir = os.path.dirname(__file__)
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
        self.app = Flask('MOCK', static_folder=os.path.join(current_dir, 'static'))
        
        self.app.jinja_env.block_start_string = '[%'
        self.app.jinja_env.block_end_string = '%]'
        self.app.jinja_env.variable_start_string = '[['
        self.app.jinja_env.variable_end_string = ']]'
        self.app.jinja_env.comment_start_string = '[#'
        self.app.jinja_env.comment_end_string = '#]'

        # async_mode = threading / eventlet / gevent / gevent_uwsgi
        self.socket_io = SocketIO(self.app, async_mode='threading', log_output=False)
        # 存储socket-io
        context.application.socket_io = self.socket_io
        # 生成过滤器实例
        if self.conf:
            self.port = self.conf.get('mock.port')
        else:
            _logger.error('Can not start mock server without config file')
            raise SyntaxError('Can not start mock server without config file.'
                              ' Default config file path = api-mock/conf.json')

        # sqlite初始化
        ROOT_DIR = application.root_dir()
        DB_FILE_NAME = 'lyrebird.db'
        SQLALCHEMY_DATABASE_URI = ROOT_DIR/DB_FILE_NAME
        # TODO: 'sqlite:///' is unfriendly to windows
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+str(SQLALCHEMY_DATABASE_URI)
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        context.db = DataBase(self.app)
        
        # 插件初始化
        plugin_manager.load()
        # 加载插件界面
        plugin_manager.add_view_to_blueprint(ui)
        # 注册插件socket事件
        plugin_manager.add_event_rules(self.socket_io)

        self.app.register_blueprint(api)
        self.app.register_blueprint(api_mock)
        self.app.register_blueprint(ui)

        @self.app.route('/')
        def index():
            """
            设置默认页面为UI首页
            """
            return redirect(url_for('ui.index'))

        @self.app.after_request
        def after_request(response: Response):
            """
            输出每条请求概要信息
            """
            lyrebird_info = response.headers.get('lyrebird', default='')
            _logger.info(f'{response.status_code} {lyrebird_info} {request.method} {request.url[:100]}')
            return response

    def run(self):
        server_ip = application.config.get('ip')    
        _logger.warning(f'start on http://{server_ip}:{self.port}')
        report_handler.start()
        # cannot import at beginning, cause db hasn't init
        from lyrebird.mock.db.models import active_db_listener
        active_db_listener()
        self.socket_io.run(self.app, host='0.0.0.0', port=self.port, debug=True, use_reloader=False)


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
