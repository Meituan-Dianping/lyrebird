import socket
from pathlib import Path
from colorama import Fore, Style
from .proxy_run import run
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.tools.cmdline import mitmdump

"""
HTTP proxy server

Default port 4272
"""

CURRENT_PATH = Path(__file__).parent
FLOW_PATH = CURRENT_PATH/'proxy_flow.py'


class LyrebirdProxyServer:

    def __init__(self, conf=None):
        self.proxy_port = str(conf.get('proxy.port', '4272')) if conf else '4272'
        '''
        --ignore_hosts:
        The ignore_hosts option allows you to specify a regex which is matched against a host:port 
        string (e.g. “example.com:443”) of a connection. Matching hosts are excluded from interception, 
        and passed on unmodified.
        
        # Ignore everything but sankuai.com, meituan.com and dianping.com:
        --ignore-hosts '^(?!.*sankuai.*)(?!.*meituan.*)(?!.*dianping.*)'
        
        According to mitmproxy docs: https://docs.mitmproxy.org/stable/howto-ignoredomains/
        '''
        self.ignore_hosts = None
        if conf.get('proxy.filters'):
            self.ignore_hosts = '^%s' % ''.join(['(?!.*%s.*)' % i for i in conf.get('proxy.filters')])
        
        self._master = None

    def start(self, callback):
        info_msg(f'start on {get_ip()}:{self.proxy_port}', f'{Fore.CYAN} ***请在被测设备上设置代理服务器地址***')
        # Open browser callback.
        callback()
        mitm_arguments = [
            '-s', str(FLOW_PATH),
            '-p', self.proxy_port,
            '--ssl-insecure',
            '-q'
        ]
        if self.ignore_hosts:
            mitm_arguments += ['--ignore-hosts', self.ignore_hosts]
        run(DumpMaster, mitmdump, mitm_arguments)


def get_ip():
    """
    获取本机ip
    这种方式，在有网络的时候相对准确一些

    :return: IP地址字符串

    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 80))
    return s.getsockname()[0]


def info_msg(*msg):
    print(f'{Fore.YELLOW}mitmproxy', *msg, Style.RESET_ALL)
