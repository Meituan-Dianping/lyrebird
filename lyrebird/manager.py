import argparse
import json
import os
import sys
import platform
import signal
import socket
import threading
import traceback
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
from lyrebird.mitm.proxy_server import LyrebirdProxyServer
from lyrebird.task import BackgroundTaskServer
from lyrebird.base_server import MultiProcessServerMessageDispatcher
from lyrebird.log import LogServer
from lyrebird.utils import RedisDict, RedisManager
from lyrebird.compatibility import compat_redis_check
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
    parser.add_argument('--extra-mock', dest='extra_mock', type=int,
                        help='Set extra mock server port, default port is 9999')
    parser.add_argument('--proxy', dest='proxy', type=int, help='Set proxy server port, default port is 4272')
    parser.add_argument('--data', dest='data', help='Set data dir, default is "./data/"')
    parser.add_argument('-b', '--no-browser', dest='no_browser',
                        action='store_true', help='Start without open a browser')
    parser.add_argument('-c', '--config', action='append', dest='config',
                        help='Start with a config file. Default is "~/.lyrebird/conf.json"')
    parser.add_argument('--log', dest='log', help='Set output log file path')
    parser.add_argument('--script', action='append', help='Set a checker script path')
    parser.add_argument('--plugin', action='append', help='Set a plugin project path')
    parser.add_argument('--database', dest='database', help='Set a database path. Default is "~/.lyrebird/lyrebird.db"')
    parser.add_argument('--es', dest='extra_string', action='append', nargs=2, help='Set a custom config')
    parser.add_argument('--no-mitm', dest='no_mitm', action='store_true', help='Start without mitmproxy on 4272')
    parser.add_argument('--enable-multiprocess', dest='enable_multiprocess', help='change event based on multithread to multiprocess(reply on redis)')
    parser.add_argument('--redis-port', dest='redis_port', type=int, help='specifies the redis service port currently in use, defalut is 6379')
    parser.add_argument('--redis-ip', dest='redis_ip', help='specifies the redis service ip currently in use, defalut is localhost')
    parser.add_argument('--redis-db', dest='redis_db', help='specifies the redis service db currently in use, defalut is 0')

    subparser = parser.add_subparsers(dest='sub_command')

    gen_parser = subparser.add_parser('gen')
    gen_parser.add_argument('path', help='Create plugin project')

    args = parser.parse_args()

    if args.version:
        print(version.LYREBIRD)
        return

    Path('~/.lyrebird').expanduser().mkdir(parents=True, exist_ok=True)

    custom_conf = {es[0]: es[1] for es in args.extra_string} if args.extra_string else {}

    # Parameters set directly through the redis command have a higher priority than those set through --es
    if args.redis_ip:
        custom_conf['redis_ip'] = args.redis_ip
    if args.redis_port:
        custom_conf['redis_port'] = args.redis_port
    if args.redis_db:
        custom_conf['redis_db'] = args.redis_db
    # --enable-multiprocess has the highest priority, 
    # When args.enable_multiprocess is None, it is controlled by config or defaults to False
    enable_multiprocess = args.enable_multiprocess.lower() if isinstance(args.enable_multiprocess, str) else None
    if enable_multiprocess == 'true' and compat_redis_check():
        custom_conf['enable_multiprocess'] = True
    elif enable_multiprocess == 'false':
        custom_conf['enable_multiprocess'] = False

    application._cm = ConfigManager(conf_path_list=args.config, custom_conf=custom_conf)

    application.sync_manager = application.SyncManager()

    # init logger for main process
    application._cm.config['verbose'] = args.verbose
    application._cm.config['log'] = args.log
    application.server['log'] = LogServer()
    application.start_log_server()
    log.init(application._cm.config, application.server['log'].queue)

    # Add exception hook
    def process_excepthook(exc_type, exc_value, tb):
        print(traceback.format_tb(tb))
    sys.excepthook = process_excepthook

    def thread_excepthook(args):
        print(f'Thread except {args}')
        print("".join(traceback.format_tb(args[2])))
    # add threading excepthook after python3.8
    if hasattr(threading, 'excepthook'):
        threading.excepthook = thread_excepthook

    # set current ip to config
    if args.ip:
        application._cm.config['ip'] = args.ip
    else:
        try:
            application._cm.config['ip'] = utils.get_ip()
        except socket.gaierror as e:
            logger.error(f'Failed to get local IP address, error occurs on {e}')

    # get all ipv4
    if not application._cm.config.get('env.ip'):
        application._cm.config['env.ip'] = utils.get_interface_ipv4()

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
    config_dict = application._cm.config.raw() if isinstance(application._cm.config, RedisDict) else application._cm.config
    config_str = json.dumps(config_dict, ensure_ascii=False, indent=4)
    logger.warning(f'Lyrebird start with config:\n{config_str}')

    # Main server
    application.server['event'] = EventServer()
    # mutilprocess message dispatcher
    application.server['dispather'] = MultiProcessServerMessageDispatcher()
    application.server['task'] = BackgroundTaskServer()

    # Start mitmproxy server
    # if set --no-mitm in commandline , skip start proxy server
    # if set proxy.no_mitm in config file, skip start proxy server
    conf_no_mitm = application._cm.config.get('proxy.no_mitm', False)
    args_no_mitm = args.no_mitm
    if args_no_mitm:
        should_start_mitm = not args_no_mitm
    else:
        should_start_mitm = not conf_no_mitm
    if should_start_mitm:
        application.status_checkpoints['mitm_proxy'] = False
        application.server['proxy'] = LyrebirdProxyServer()

    application.server['extra.mock'] = ExtraMockServer()
    application.server['db'] = LyrebirdDatabaseServer(path=args.database)
    if not hasattr(application.server['db'], 'session'):
        return
    application.server['plugin'] = PluginManager()
    application.server['checker'] = LyrebirdCheckerServer()

    # Mock mush init after other servers
    application.server['mock'] = LyrebirdMockServer()

    # int statistics reporter
    application.server['reporter'] = reporter.Reporter()
    application.reporter = application.server['reporter']

    # handle progress message
    application.process_status_listener()

    # Start server without mock server, mock server must start after all blueprint is done
    application.start_server_without_mock_and_log()
    
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

    if application.config.get('enable_multiprocess', False):
        application.server['event'].async_start()

    # Start server without mock server, mock server must start after all blueprint is done
    application.start_mock_server()

    # auto open web browser
    application.NO_BROSWER = args.no_browser

    # main process is ready, publish system event
    application.status_ready()

    # stop event handler
    def signal_handler(signum, frame):
        application.stop_server()
        application.terminate_server()
        application.sync_manager.destory()
        if application.config.get('enable_multiprocess', False):
            RedisManager.destory()
        threading.Event().set()
        print('!!!Ctrl-C pressed. Lyrebird stop!!!')
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
