import json
import os
import sys
import socket
import errno
import socket
import subprocess
from .logger_helper import get_logger, _print_error
from . import plugin_manager
from flask import Flask, request, redirect, url_for, Response
from . import context
from .blueprints.api import api
from .blueprints.ui import ui
from .blueprints.api_mock import api_mock
from .console_helper import warning_msg, mock_msg, err_msg, url_color, tag_green
from flask_socketio import SocketIO
from .reporter import report_handler
from ..version import VERSION
import datetime

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
_logger = get_logger()


class LyrebirdMockServer:
    """
    模拟接口服务
    使用flask在默认的9090端口启动，模拟线上接口，同时支持通过api动态修改接口数据。

    """
    def __init__(self, conf=None, verbose=False, block=False):
        self.block = block
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
        # 加载verbose设置
        context.application.verbose = verbose
        # 生成过滤器实例
        if conf:
            context.application.conf = conf
            self.port = conf.get('mock.port')
            warning_msg(f'Load config : {json.dumps(conf, ensure_ascii=False, indent=4)}')
        else:
            err_msg('Can not start mock server without config file')
            raise SyntaxError('Can not start mock server without config file.'
                              ' Default config file path = api-mock/conf.json')

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


    def start(self):
        server_ip = context.application.conf.get('ip')
        warning_msg(f'start on {server_ip}:{self.port}')
        import threading
        self._working_thread = threading.Thread(
            target=self.socket_io.run,
            args=(self.app,),
            kwargs=dict(host='0.0.0.0', port=self.port, debug=True, use_reloader=False),
            name='MOCK_SERVER',
            daemon=True)
        self._working_thread.start()

        report_handler.start()


    def stop(self):
        """
        停止服务

        """
        try:
            self.socket_io.stop()
        except Exception:
            pass
        report_handler.stop()
        warning_msg('MockServer shutdown')
