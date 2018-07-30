import os
import sys
from signal import SIGTERM
import signal
import socket
import fire
from lyrebird import config
from .mock.logger_helper import init_logger_settings
from .mock import mock_server
from .proxy import proxy_server
import webbrowser
import threading
from lyrebird.project_builder.builder import PluginProjectBuilder

"""
Lyrebird main entry

"""

class ManagerError(Exception):
    pass


class Server:
    """
    Lyrebird server class

    useage:
        import lyrebird
        
        server = lyrebird.Server()
        server.start()
    """

    def __init__(self):
        self.verbose = False
        self.record = False
        self.custom_conf_name = None
        self._conf = None
        self._pid = None
        self._mock_port = None
        self._proxy_port = None
        self._data_root_dir = None
        self.mock_server = None
        self.proxy_server = None
        self._conf_manager = None
        self.pid_file_name = None

    def v(self):
        """
        是否显示详细日志

        """
        self.verbose = True

    def mock_port(self, port):
        self._mock_port = port
        return self

    def proxy_port(self, port):
        self._proxy_port = port
        return self

    def data_root_dir(self, path):
        self._data_root_dir = path
        return self

    def set_cache_uri(self, uri):
        self._conf_manager = config.Config(name=self.pid_file_name)
        self._conf_manager.init()
        cache = self._conf_manager.load_cache()
        cache['user_data_uri'] = uri
        self._conf_manager.save_cache(cache)

    def init_conf(self):
        self._conf_manager = config.Config(name=self.pid_file_name)
        self._conf_manager.init()
        self._conf_manager.save_pid()

        custom_args = {}

        if self._mock_port:
            custom_args['mock.port'] = self._mock_port
        if self._proxy_port:
            custom_args['proxy.port'] = self._proxy_port
        if self._data_root_dir:
            custom_args['mock.data'] = self._data_root_dir

        cache = self._conf_manager.load_cache()

        if self.custom_conf_name == None:
            self.custom_conf_name = cache.get('custom_conf')
        else:
            cache['custom_conf'] = self.custom_conf_name
            self._conf_manager.save_cache(cache)

        if cache.get('user_data_uri'):
            self._conf_manager.download(cache.get('user_data_uri'))

        self._conf = self._conf_manager.load_tmp(self.custom_conf_name, **custom_args)
        self._conf['ip'] = get_ip()

    def start(self, callback):
        """
        启动proxy&mock

        
        self.mock_server = mock_server.LyrebirdMockServer(conf, self.verbose)
        self.mock_server.start()
        self.proxy_server = proxy_server.LyrebirdProxyServer(conf, self.verbose)
        self.proxy_server.start()

        :return: 
        """
        init_logger_settings(verbose=self.verbose)
        self.init_conf()
        self.mock_server = mock_server.LyrebirdMockServer(self._conf, self.verbose)
        self.mock_server.start()
        self.proxy_server = proxy_server.LyrebirdProxyServer(self._conf)
        self.proxy_server.start(callback)

    def stop(self):
        if self.mock_server:
            self.mock_server.stop()


class CommandLine:
    """
    命令行入口
    
    * lyrebird
    以缺省参数启动lyrebird

    * lyrebird start
    以缺省参数启动lyrebird

    * lyrebird v start
    以输出详细日志模式启动lyrebird

    * lyrebird no-browser start
    启动lyrebird不默认打开浏览器

    * lyrebird start --mock 9090 --proxy 4272 --data .
    指定参数启动lyrebird
    参数：
        --mock 默认9090 ， mock服务及前端端口
        --proxy 默认4272， 代理服务端口
        --data 默认./data, mock数据根目录
        --name 默认lyrebird，服务别名（用于通过别名停止指定的lyrebird服务）

    * lyrebird stop
    停止lyrebird

    * lyrebird stop --name foo
    停止别名为foo的lyrebird
    """
    def __init__(self):
        self._open_browser = True
        self.server = Server()

    def v(self):
        self.server.v()
        return self

    def no_browser(self):
        self._open_browser = False
        return self

    def start(self, mock=None, proxy=None, data=None, name='lyrebird', config=None):
        if mock:
            self.server.mock_port(mock)
        if proxy:
            self.server.proxy_port(proxy)
        if data:
            self.server.data_root_dir(data)
        if name:
            self.server.pid_file_name = name
        if config:
            self.server.custom_conf_name = config

        # open browser
        def open_browser():
            if self._open_browser:
                webbrowser.open('http://localhost:' + str(self.server._conf.get('mock.port')))

        def signal_handler(signum, frame):
            print('\n!!!Ctrl-C pressed. Lyrebird stop!!!')
            self.server.stop()
            threading.Event().set()
            os._exit(1)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        self.server.start(callback=open_browser)

    def stop(self, name='lyrebird'):
        try:
            os.kill(config.Config(name=name).read_pid(), SIGTERM)
        except Exception:
            # 未找到进程时不处理
            pass
        config.Config(name=name).remove_pid()

    def resource(self, uri=None, branch='master'):
        if uri:
            uri = '%s --branch %s' % (uri, branch)
            self.server.set_cache_uri(uri)
        else:
            print('\nResource uri is not set!')


def debug():
    CommandLine().v().start()


def run():
    if len(sys.argv) == 1:
        fire.Fire(CommandLine, 'v start')
    else:
        fire.Fire(CommandLine)


def plugin():
    fire.Fire(PluginProjectBuilder)


def get_ip():
    """
    获取当前设备在网络中的ip地址

    :return: IP地址字符串
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('meituan.com', 80))
    return s.getsockname()[0]