from pathlib import Path
from lyrebird import log
import subprocess
import os
import json
import sys
import shutil
import tarfile
import requests
import click
import tempfile
import time
from lyrebird.base_server import ProcessServer

"""
HTTP proxy server
Default port 4272
"""


class LyrebirdProxyServer(ProcessServer):

    def get_mitmdump_filename(self):
        platform = sys.platform
        if platform in ['linux', 'darwin']:
            return 'mitmdump'
        elif platform.startswith('win'):
            return 'mitmdump.exe'
        else:
            raise UnsupportedPlatform(f'platform name: {platform}')

    def find_mitmdump_in_path(self):
        mitmdump_path = shutil.which('mitmdump')
        if not mitmdump_path:
            return None

        mitmdump = Path(mitmdump_path)
        if mitmdump.exists() and mitmdump.is_file():
            return mitmdump
        else:
            return None

    def find_mitmdump_in_lyrebird_home(self):
        mitmdump = Path('~/.lyrebird/bin').expanduser().absolute()/self.get_mitmdump_filename()
        if mitmdump.exists() and mitmdump.is_file():
            return mitmdump
        else:
            return None

    def download_mitmproxy(self):
        '''
        Download mitmdump 8.1.1 from mitmproxy.org
        New file will be write in to ~/.lyrebird/bin
        Support Window Linux and OSX
        '''
        platform = sys.platform
        if platform == 'linux':
            download_url = 'https://snapshots.mitmproxy.org/8.1.1/mitmproxy-8.1.1-linux.tar.gz'
        elif platform == 'darwin':
            download_url = 'https://snapshots.mitmproxy.org/8.1.1/mitmproxy-8.1.1-osx.tar.gz'
        elif platform.startswith('win'):
            download_url = 'https://snapshots.mitmproxy.org/8.1.1/mitmproxy-8.1.1-windows.zip'
        else:
            raise UnsupportedPlatform(f'unsupport platform: {platform}')

        resp = requests.get(download_url, stream=True)
        content_length = int(resp.headers.get('content-length'))
        click.secho(f'\nmitmdupm not found\nStart downloading mitmproxy: {download_url}')
        with click.progressbar(length=content_length) as bar, tempfile.NamedTemporaryFile('w+b') as tempf:
            for chunk in resp.iter_content(4*2048):
                tempf.write(chunk)
                bar.update(len(chunk))
            tempf.flush()
            tempf.seek(0)

            tarf = tarfile.open(fileobj=tempf.file)
            mitmdump_filename = self.get_mitmdump_filename()
            tarf.extract(mitmdump_filename, str(Path('~/.lyrebird/bin/').expanduser().absolute()))
            mitmdump_filepath = f'~/.lyrebird/bin/{mitmdump_filename}'
            click.secho(f'\n🍺 Download completed: write to {mitmdump_filepath}')
            return mitmdump_filepath

    def show_mitmdump_help(self, config, logger):
        proxy_port = config['proxy.port']
        errmsg = f'Download mitmproxy fail.\nCan\'t start HTTP proxy server on {proxy_port}\nPlease install mitmproxy(https://mitmproxy.org/) and restart lyrebird\n'
        logger.error(errmsg)
        return errmsg

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

    def start_mitmdump(self, queue, config, mitmdump_path, logger):
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
            logger.log(60, f'HTTP proxy server start on {proxy_port}')
        else:
            self.show_mitmdump_start_timeout_help(mitmdump_path, logger)

    def run(self, queue, config, *args, **kwargs):
        # Init logger
        log.init(config)
        logger = log.get_logger()
        # Find mitmproxy in sys path
        mitmdump_path = self.find_mitmdump_in_path()
        if not mitmdump_path:
            # Find mitmproxy in ~/.lyrebird/bin
            mitmdump_path = self.find_mitmdump_in_lyrebird_home()
        if not mitmdump_path:
            # Download mitmproxy and save in ~/.lyrebird/bin
            mitmdump_path = self.download_mitmproxy()
        if not mitmdump_path:
            # Start HTTP proxy server failed
            # mitmdump not found
            self.show_mitmdump_help(config, logger)
            return
        self.start_mitmdump(queue, config, mitmdump_path, logger)


class UnsupportedPlatform(Exception):
    pass
