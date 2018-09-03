import argparse
import webbrowser
import json
import traceback
import socket
import threading
import signal
import os
from lyrebird import log
from lyrebird import application
from lyrebird.config import Rescource, ConfigManager
from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird.proxy.proxy_server import LyrebirdProxyServer
from lyrebird.event import EventServer
from lyrebird.task import BackgroundTaskServer


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

    parser.add_argument('-v', dest='verbose', action='store_true', help='Show verbose log')
    parser.add_argument('--mock', dest='mock', type=int, help='Set mock server port, default port is 4272')
    parser.add_argument('--proxy', dest='proxy', type=int, help='Set proxy server port, default port is 9090')
    parser.add_argument('--data', dest='data', help='Set data dir, default is "./data/"')
    parser.add_argument('-b', '--no_browser', dest='no_browser', action='store_true', help='Start without open a browser')
    parser.add_argument('-c', '--config', dest='config', help='Start with a config file. Default is "~/.lyrebird/conf.json"')
    parser.add_argument('--log', dest='log', help='Set output log file path')

    subparser = parser.add_subparsers(dest='sub_command')
    src_parser = subparser.add_parser('src')
    src_parser.add_argument('uri')
    subparser.add_parser('plugin')

    args = parser.parse_args()

    if args.config:
        application._cm = ConfigManager(conf_path=args.config)
    else:
        application._cm = ConfigManager()
    application._src = Rescource()

    # set current ip to config
    try:
        application._cm.config['ip'] = _get_ip()
    except socket.gaierror as e:
        logger.error('Failed to get local IP address, error occurs on %s' % e)

    if args.verbose:
        application._cm.config['verbose'] = True

    # init file logger after config init
    log.init(args.log)
    
    if args.mock:
        application._cm.config['mock.port'] = args.mock
    if args.proxy:
        application._cm.config['proxy.port'] = args.proxy
    if args.data:
        application._cm.config['mock.data'] = args.data

    logger.debug(f'Read args: {args}')

    if args.sub_command == 'src':
        logger.debug('EXEC SUBCMD:SRC')
        src(args)
    elif args.sub_command == 'plugin':
        logger.debug('EXEC SUBCMD:PLUGIN')
        plugin(args)
    else:
        logger.debug('EXEC LYREBIRD START')
        run(args)


def run(args:argparse.Namespace):
    # show current config contents
    config_str = json.dumps(application._cm.config, ensure_ascii=False, indent=4)
    logger.warning(f'Lyrebird start with config:\n{config_str}')
        
    application.server['event'] = EventServer()
    application.server['task'] = BackgroundTaskServer()
    application.server['proxy'] = LyrebirdProxyServer()   
    application.server['mock'] = LyrebirdMockServer()

    application.start_server()

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


def debug():
    # use lyrebird.debug to start plugin in debug mode
    # can pass args by sys.args
    main()
    # main thread loop
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_forever()


def plugin(args:argparse.Namespace):
    pass


def src(args:argparse.Namespace):
    from threading import Thread
    def worker():
        application._src.download(args.uri)
    Thread(target=worker).start()


def _get_ip():
    """
    Get local ip from socket connection

    :return: IP Addr string
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('meituan.com', 80))
    return s.getsockname()[0]
