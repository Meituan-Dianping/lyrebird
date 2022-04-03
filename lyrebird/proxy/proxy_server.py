from pathlib import Path
from colorama import Fore
from lyrebird.base_server import ThreadServer
from lyrebird import application
from lyrebird.log import get_logger
import multiprocessing
import os
import json


"""
HTTP proxy server

Default port 4272
"""
logger = get_logger()


CURRENT_PATH = Path(__file__).parent
SCRIPT_FILE = CURRENT_PATH/'mitm_script.py'
MITMDUMP_FILE = CURRENT_PATH/'mitm_exec.py'


def run_mitmproxy(**kwargs):
    import sys
    from mitmproxy.tools.main import mitmdump

    custom_env = kwargs.get('env')
    os.environ.update(custom_env)

    args = kwargs.get('args')

    sys.argv = ['mitmdump.py', *args]
    sys.exit(mitmdump())


class LyrebirdProxyServer():

    def __init__(self):
        super().__init__()

        conf = application.config
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
        self.ignore_hosts = conf.get('proxy.ignore_hosts', None)
        self._proxy_server_process = None

    def start(self):
        server_ip = application.config.get('ip')
        # info_msg(f'start on {server_ip}:{self.proxy_port}', f'{Fore.CYAN} ***请在被测设备上设置代理服务器地址***')
        logger.warning(f'start on http://{server_ip}:{self.proxy_port}   {Fore.CYAN} ***请在被测设备上设置代理服务器地址***')
        mitm_arguments = [
            '-s', str(SCRIPT_FILE),
            '-p', self.proxy_port,
            '--ssl-insecure',
            '--no-http2',
            '-q',
            '--set',
            'block_global=false'
        ]
        if self.ignore_hosts:
            mitm_arguments += ['--ignore-hosts', self.ignore_hosts]
        mitmenv = os.environ
        mitmenv['PROXY_PORT'] = str(application.config.get('mock.port', 9090))
        mitmenv['PROXY_FILTERS'] = json.dumps(application.config.get('proxy.filters', []))

        self._proxy_server_process = multiprocessing.Process(
            group=None,
            target=run_mitmproxy,
            kwargs={
                'env': {
                    'PROXY_PORT': str(application.config.get('mock.port', 9090)),
                    'PROXY_FILTERS': json.dumps(application.config.get('proxy.filters', []))
                },
                'args': mitm_arguments})
        self._proxy_server_process.start()

    def stop(self):
        if self._proxy_server_process:
            self._proxy_server_process.terminate()
            logger.warning('ProxyServer shutdown')
