from pathlib import Path
from lyrebird import log
import subprocess
import os
import json
import requests
import time
from lyrebird.base_server import ProcessServer
from lyrebird.mitm.mitm_installer import init_mitm

"""
HTTP proxy server
Default port 4272
"""


class LyrebirdProxyServer(ProcessServer):

    def __init__(self):
        super().__init__()
        self.mitm_path = init_mitm()
        self.kwargs['mitm_path'] = self.mitm_path

    def show_mitmdump_start_timeout_help(self, mitmdump_filepath, logger):
        logger.error(f'Start mitmdump failed.\nPlease check your mitmdump file {mitmdump_filepath}')

    def wait_for_mitm_start(self, config, logger):
        timeout = 30
        wait_time_count = 0
        mock_port = config.get('mock.port')
        proxy_port = config.get('proxy.port')
        while True:
            if wait_time_count >= timeout:
                return False

            time.sleep(1)
            wait_time_count += 1
            try:
                resp = requests.get(f'http://127.0.0.1:{mock_port}/api/status',
                                    proxies={'http': f'http://127.0.0.1:{proxy_port}'})
                if resp.status_code != 200:
                    continue
                else:
                    return True
            except Exception:
                continue

    def start_mitmdump(self, queue, config, logger, mitmdump_path):
        proxy_port = config.get('proxy.port', 4272)
        mock_port = config.get('mock.port', 9090)
        '''
        --ignore_hosts:
        The ignore_hosts option allows you to specify a regex which is matched against a host:port
        string (e.g. “example.com:443”) of a connection. Matching hosts are excluded from interception,
        and passed on unmodified.

        # Ignore everything but sankuai.com, meituan.com and dianping.com:
        --ignore-hosts '^(?!.*sankuai.*)(?!.*meituan.*)(?!.*dianping.*)'

        According to mitmproxy docs: https://docs.mitmproxy.org/stable/howto-ignoredomains/
        '''
        ignore_hosts = config.get('proxy.ignore_hosts', None)

        current_path = Path(__file__).parent
        script_path = current_path/'mitm_script.py'

        mitm_arguments = [
            '-s', str(script_path),
            '-p', str(proxy_port),
            '--ssl-insecure',
            '--no-http2',
            '-q',
            '--set',
            'block_global=false'
        ]
        if ignore_hosts:
            mitm_arguments += ['--ignore-hosts', ignore_hosts]
        mitmenv = os.environ
        mitmenv['PROXY_PORT'] = str(mock_port)
        mitmenv['PROXY_FILTERS'] = json.dumps(config.get('proxy.filters', []))
        logger.info('HTTP proxy server starting...')
        subprocess.Popen(f'{str(mitmdump_path)} {" ".join(mitm_arguments)}', shell=True, env=mitmenv)
        is_mitm_start = self.wait_for_mitm_start(config, logger)
        if is_mitm_start:
            self.publish_init_status(queue, 'READY')
            logger.log(60, f'HTTP proxy server start on {proxy_port}')
        else:
            self.publish_init_status(queue, 'ERROR')
            self.show_mitmdump_start_timeout_help(mitmdump_path, logger)

    def publish_init_status(self, queue, status):
        queue.put({
            'type': 'event',
            "channel": "system",
            "content": {
                'system': {
                    'action': 'init_module',
                    'status': status,
                    'module': 'mitm_proxy'
                }
            }
        })

    def run(self, queue, config, *args, **kwargs):
        # Init logger
        log.init(config)
        logger = log.get_logger()
        mitm_path = kwargs.get('mitm_path')
        self.start_mitmdump(queue, config, logger, mitm_path)


class UnsupportedPlatform(Exception):
    pass
