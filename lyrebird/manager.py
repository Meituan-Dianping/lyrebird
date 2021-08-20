import argparse
import json
import os
import platform
import signal
import socket
import threading
import traceback
import webbrowser
from pathlib import Path

from packaging.version import parse as vparse

from lyrebird import application, log, project_builder, reporter, version
from lyrebird.checker import LyrebirdCheckerServer
from lyrebird.config import ConfigManager
from lyrebird.db.database_server import LyrebirdDatabaseServer
from lyrebird.event import EventServer
from lyrebird.mock.dm.label import LabelHandler
from lyrebird.mock.extra_mock_server import ExtraMockServer
from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder
from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird.notice_center import NoticeCenter
from lyrebird.plugins import PluginManager
from lyrebird.proxy.proxy_server import LyrebirdProxyServer
from lyrebird.task import BackgroundTaskServer
from lyrebird import utils


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
    parser.add_argument('--ip', dest='ip', help='Set device ip')
    parser.add_argument('--mock', dest='mock', type=int, help='Set mock server port, default port is 9090')
    parser.add_argument('--extra-mock', dest='extra_mock', type=int, help='Set extra mock server port, default port is 9999')
    parser.add_argument('--proxy', dest='proxy', type=int, help='Set proxy server port, default port is 4272')
    parser.add_argument('--data', dest='data', help='Set data dir, default is "./data/"')
    parser.add_argument('-b', '--no_browser', dest='no_browser',
                        action='store_true', help='Start without open a browser')
    parser.add_argument('-c', '--config', dest='config',
                        help='Start with a config file. Default is "~/.lyrebird/conf.json"')
    parser.add_argument('--log', dest='log', help='Set output log file path')
    parser.add_argument('--script', action='append', help='Set a checker script path')
    parser.add_argument('--plugin', action='append', help='Set a plugin project path')
    parser.add_argument('--database', dest='database', help='Set a database path. Default is "~/.lyrebird/lyrebird.db"')
    parser.add_argument('--es', dest='extra_string', action='append', nargs=2, help='Set a custom config')

    subparser = parser.add_subparsers(dest='sub_command')

    gen_parser = subparser.add_parser('gen')
    gen_parser.add_argument('path', help='Create plugin project')

    args = parser.parse_args()

    if args.version:
        print(version.LYREBIRD)
        return

    Path('~/.lyrebird').expanduser().mkdir(parents=True, exist_ok=True)

    custom_conf = {es[0]:es[1] for es in args.extra_string} if args.extra_string else None
    application._cm = ConfigManager(conf_path=args.config, custom_conf=custom_conf)

    # set current ip to config
    if args.ip:
        application._cm.config['ip'] = args.ip
    else:
        try:
            application._cm.config['ip'] = _get_ip()
        except socket.gaierror as e:
            logger.error(f'Failed to get local IP address, error occurs on {e}')

    # init file logger after config init
    application._cm.config['verbose'] = args.verbose
    log.init(args.log)

    if args.mock:
        application._cm.config['mock.port'] = args.mock
    if args.proxy:
        application._cm.config['proxy.port'] = args.proxy
    if args.data:
        application._cm.config['mock.data'] = str(Path(args.data).expanduser().absolute())

    # Set extra mock port
    if args.extra_mock:
        _extra_mock_port = args.extra_mock
    else:
        _extra_mock_port = 9999
    if utils.is_port_in_use(_extra_mock_port):
        _extra_mock_port = utils.find_free_port()
    application._cm.config['extra.mock.port'] = _extra_mock_port

    logger.debug(f'Read args: {args}')

    if args.sub_command == 'gen':
        logger.debug('EXEC: Plugin project generator')
        gen(args)
    else:
        logger.debug('EXEC: LYREBIRD START')
        run(args)


def run(args: argparse.Namespace):
    sys_name = platform.system()
    if sys_name.lower() != 'windows':
        import resource

        # Set file descriptors
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (8192, 8192))
        except Exception:
            traceback.print_exc()
            logger.warning('Set file descriptors failed\nPlease set it by your self, use "ulimit -n 8192" with root account')

    # show current config contents
    print_lyrebird_info()
    config_str = json.dumps(application._cm.config, ensure_ascii=False, indent=4)
    logger.warning(f'Lyrebird start with config:\n{config_str}')

    # Main server
    application.server['event'] = EventServer()

    application.server['task'] = BackgroundTaskServer()
    application.server['proxy'] = LyrebirdProxyServer()
    application.server['mock'] = LyrebirdMockServer()
    application.server['extra.mock'] = ExtraMockServer()
    application.server['db'] = LyrebirdDatabaseServer(path=args.database)
    application.server['plugin'] = PluginManager()
    application.server['checker'] = LyrebirdCheckerServer()

    application.start_server()

    # int statistics reporter
    application.reporter = reporter.Reporter()
    reporter.start()
    # activate notice center
    application.notice = NoticeCenter()

    # init label handler
    application.labels = LabelHandler()

    # init encoder&decoder
    application.encoders_decoders = EncoderDecoder()

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

    # Lyrebird status contains: 'READY' and 'INITING'
    application.status = 'READY'

    # stop event handler
    def signal_handler(signum, frame):
        reporter.stop()
        application.stop_server()
        threading.Event().set()
        logger.warning('!!!Ctrl-C pressed. Lyrebird stop!!!')
        os._exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    threading.Event().wait()


def gen(args):
    parent_path = args.path
    project_name = input('Please input your project name:')
    if not project_name:
        print('Not set project name')
        return
    project_builder.make_plugin_project(project_name, parent_path+'/'+project_name)


def _get_ip():
    """
    Get local ip from socket connection

    :return: IP Addr string
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('bing.com', 80))
    return s.getsockname()[0]


def print_lyrebird_info():
    logo = [
        "",
        "",
        "     _                    _     _         _ ",
        "    | |                  | |   (_)       | |",
        "    | |    _   _ _ __ ___| |__  _ _ __ __| |",
        "    | |   | | | | '__/ _ \\ '_ \\| | '__/ _' |",
        "    | |___| |_| | | |  __/ |_) | | | | (_| |",
        "    \\_____/\\__, |_|  \\___|_.__/|_|_|  \\__,_|",
        "            __/ |                           ",
        "           |___/                            ",
        "",
        f"                   v{version.VERSION}",
        "",
        "",
        ""
    ]
    logo_str = '\n'.join(logo)
    # Custom log level 60  : NOTICE
    logger.log(60, logo_str)
