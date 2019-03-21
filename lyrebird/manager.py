import argparse
import webbrowser
import json
import socket
import threading
import signal
import os
from pathlib import Path
from lyrebird import log
from lyrebird import application
from lyrebird.config import Rescource, ConfigManager
from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird.proxy.proxy_server import LyrebirdProxyServer
from lyrebird.event import EventServer
from lyrebird.task import BackgroundTaskServer
from lyrebird.notice_center import NoticeCenter
from lyrebird.db.database_server import LyrebirdDatabaseServer
from lyrebird.plugins import PluginManager
from lyrebird.checker import LyrebirdCheckerServer
from lyrebird import version


logger = log.get_logger()


def main():
    """
    Command line main entry

    Start lyrebird

    * start in default config
    ```
    lyrebird
    ```
    * start with verbose mode
    ```
    lyrebird -v
    ```
    * start without open a web browser
    ```
    lyrebird -b
    ```
    * start with a specified config file
    ```
    lyrebird -c /path/to/your/config/file
    ```
    * start with multipart args
    ```
    lyrebird -v --mock 8080 -c /path/to/your/config/file
    ```
    """
    parser = argparse.ArgumentParser(prog='lyrebird')

    parser.add_argument('-V', '--version', dest='version', action='store_true', help='show lyrebird version')
    parser.add_argument('-v', dest='verbose', action='count', default=0, help='Show verbose log')
    parser.add_argument('--mock', dest='mock', type=int, help='Set mock server port, default port is 4272')
    parser.add_argument('--proxy', dest='proxy', type=int, help='Set proxy server port, default port is 9090')
    parser.add_argument('--data', dest='data', help='Set data dir, default is "./data/"')
    parser.add_argument('-b', '--no_browser', dest='no_browser', action='store_true', help='Start without open a browser')
    parser.add_argument('-c', '--config', dest='config', help='Start with a config file. Default is "~/.lyrebird/conf.json"')
    parser.add_argument('--log', dest='log', help='Set output log file path')
    parser.add_argument('--script', action='append', help='Set a checker script path')
    parser.add_argument('--plugin', action='append', help='Set a plugin project path')

    subparser = parser.add_subparsers(dest='sub_command')
    subparser.add_parser('gen')

    args = parser.parse_args()

    if args.version:
        print(version.LYREBIRD)
        return

    if args.config:
        application._cm = ConfigManager(conf_path=args.config)
    else:
        application._cm = ConfigManager()

    # set current ip to config
    try:
        application._cm.config['ip'] = _get_ip()
    except socket.gaierror as e:
        logger.error('Failed to get local IP address, error occurs on %s' % e)

    # init file logger after config init
    application._cm.config['verbose'] = args.verbose
    log.init(args.log)
    
    if args.mock:
        application._cm.config['mock.port'] = args.mock
    if args.proxy:
        application._cm.config['proxy.port'] = args.proxy
    if args.data:
        application._cm.config['mock.data'] = args.data

    logger.debug(f'Read args: {args}')

    if args.sub_command == 'gen':
        logger.debug('EXEC: Plugin project generator')
        gen(args)
    else:
        logger.debug('EXEC: LYREBIRD START')
        run(args)


def run(args:argparse.Namespace):
    # Check mock data group version. Update if is older than 1.x
    from . import mock_data_formater
    data_path = application._cm.config['mock.data']
    data_dir = Path(data_path)
    mock_data_formater.check_data_dir(data_dir)

    # show current config contents
    config_str = json.dumps(application._cm.config, ensure_ascii=False, indent=4)
    logger.warning(f'Lyrebird start with config:\n{config_str}')

    # Main server
    application.server['event'] = EventServer()
    
    application.server['task'] = BackgroundTaskServer()
    application.server['proxy'] = LyrebirdProxyServer()
    application.server['mock'] = LyrebirdMockServer()
    application.server['db'] = LyrebirdDatabaseServer()
    application.server['plugin'] = PluginManager()
    application.server['checker'] = LyrebirdCheckerServer()

    application.start_server()

    # activate notice center
    application.notice = NoticeCenter()

    # load debug plugin
    # TODO
    plugin_manager = application.server['plugin']
    if args.plugin:
        plugin_manager.plugin_path_list += args.plugin
    plugin_manager.reload()

    # load debug script
    if args.script:
        application.server['checker'].load_scripts(args.script)

    # auto open web browser
    if not args.no_browser:
        webbrowser.open(f'http://localhost:{application.config["mock.port"]}')

    # stop event handler
    def signal_handler(signum, frame):
        application.stop_server()
        threading.Event().set()
        logger.warning('!!!Ctrl-C pressed. Lyrebird stop!!!')
        os._exit(1)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    threading.Event().wait()


def gen(args):
    pass


def _get_ip():
    """
    Get local ip from socket connection

    :return: IP Addr string
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('bing.com', 80))
    return s.getsockname()[0]
