import logging
from lyrebird import application
from .base_server import ProcessServer
from logging.handlers import TimedRotatingFileHandler
from colorama import Fore, Style, Back
from collections import namedtuple
from pathlib import Path
import signal
import os
DEFAULT_LOG_PATH = '~/.lyrebird/lyrebird.log'
LOGGER_INITED = False

Color = namedtuple('Color', ['fore', 'style', 'back'])

COLORS = dict(
    NOTICE=Color(fore=Fore.GREEN, style=Style.NORMAL, back=Back.RESET),
    CRITICAL=Color(fore=Fore.WHITE, style=Style.BRIGHT, back=Back.RED),
    ERROR=Color(fore=Fore.RED, style=Style.NORMAL, back=Back.RESET),
    WARNING=Color(fore=Fore.YELLOW, style=Style.NORMAL, back=Back.RESET),
    INFO=Color(fore=Fore.WHITE, style=Style.NORMAL, back=Back.RESET),
    DEBUG=Color(fore=Fore.GREEN, style=Style.NORMAL, back=Back.RESET)
)

process = None
queue_handler = None


def colorit(message, levelname):
    color = COLORS.get(levelname)
    if color:
        return f'{color.fore}{color.style}{color.back}{message}{Style.RESET_ALL}'
    else:
        return message


def info_color(message):
    return f'{Fore.WHITE}{Style.DIM}{Back.RESET}{message}{Style.RESET_ALL}'


class ColorFormater(logging.Formatter):

    def format(self, record: logging.LogRecord):
        s = self.formatTime(record)
        fmt_log = info_color(f'{s} {record.pathname}:{record.lineno}\n') + \
            colorit(f'{record.levelname} {record.msg}', record.levelname)
        return fmt_log


def make_stream_handler():
    color_formater = ColorFormater()
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(color_formater)
    return stream_handler


def make_file_handler(_log_path=None):
    # Set default value
    if not check_path(_log_path):
        _log_path = DEFAULT_LOG_PATH

    # Add pid and thread name in log file
    file_formater = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] [PID]%(process)s::%(threadName)s (%(pathname)s)  %(message)s'
    )
    log_file = Path(_log_path).expanduser().absolute().resolve()

    file_handler = TimedRotatingFileHandler(log_file, backupCount=1, encoding='utf-8', when='midnight')
    file_handler.setFormatter(file_formater)
    return file_handler


def check_path(path):
    if not path:
        return False
    if not os.path.exists(os.path.dirname(path)):
        return False
    if os.path.isdir(path) or path.split('.')[-1] != 'log':
        return False
    return True


def init(config, log_queue = None):
    global LOGGER_INITED
    global queue_handler
    if LOGGER_INITED:
        return
    
    if not config:
        config = {}
    
    if not log_queue:
        log_server = LogServer()
        log_queue = log_server.queue

    logging.addLevelName(60, 'NOTICE')

    verbose = config.get('verbose', 0)
    if verbose == 0:
        logger_level = logging.ERROR
    elif verbose == 1:
        logger_level = logging.INFO
    elif verbose >= 2:
        logger_level = logging.DEBUG

    queue_handler = logging.handlers.QueueHandler(log_queue)

    for _logger_name in ['lyrebird', 'socketio', 'engineio', 'mock', 'werkzeug', 'flask']:
        _logger = logging.getLogger(_logger_name)
        _logger.addHandler(queue_handler)
        _logger.setLevel(logger_level)
    
    LOGGER_INITED = True


class LogServer(ProcessServer):

    _instance = None

    def __init__(self):
        super().__init__()
        self.queue = application.sync_manager.get_multiprocessing_queue()
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def run(self, async_obj, config, *args, **kwargs):
        log_queue = async_obj['logger_queue']

        signal.signal(signal.SIGINT, signal.SIG_IGN)

        logging.addLevelName(60, 'NOTICE')

        stream_handler = make_stream_handler()

        log_path = config.get('log')
        file_handler = make_file_handler(log_path)

        verbose = config.get('verbose', 0)
        if verbose == 0:
            logger_level = logging.ERROR
        elif verbose == 1:
            logger_level = logging.INFO
        elif verbose >= 2:
            logger_level = logging.DEBUG

        lyrebird_logger = logging.getLogger('lyrebird')
        lyrebird_logger.addHandler(stream_handler)
        lyrebird_logger.addHandler(file_handler)
        lyrebird_logger.setLevel(logger_level)

        for _logger_name in ['socketio', 'engineio', 'mock', 'werkzeug', 'flask']:
            _logger = logging.getLogger(_logger_name)
            _logger.addHandler(file_handler)
            _logger.setLevel(logger_level)
        
        if log_path and not check_path(log_path):
            lyrebird_logger.warning(f'Illegal log path: {log_path}, log file path have changed to the default path: {DEFAULT_LOG_PATH}')
        
        self.running = True

        while self.running:
            try:
                log = log_queue.get()
                if log is None:
                    break
                logger = logging.getLogger(log.name)
                logger.handle(log)
            except KeyboardInterrupt:
                break
    
    def stop(self):
        super().stop()
        self.queue = None
        logging.shutdown()
        for _logger_name in ['lyrebird', 'socketio', 'engineio', 'mock', 'werkzeug', 'flask']:
            logger = logging.getLogger(_logger_name)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            logger.setLevel(logging.CRITICAL)
    
    def terminate(self):
        super().terminate()
        logging.shutdown()


def get_logger():
    return logging.getLogger('lyrebird')
