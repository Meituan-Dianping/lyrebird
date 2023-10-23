import logging
from .base_server import ProcessServer
from multiprocessing import Queue, Lock
from logging.handlers import TimedRotatingFileHandler
from colorama import Fore, Style, Back
from collections import namedtuple
from pathlib import Path
import os
DEFAULT_LOG_PATH = '~/.lyrebird/lyrebird.log'
LOGGER_INITED = False
log_process_lock = Lock()

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
    if not _log_path:
        _log_path = DEFAULT_LOG_PATH

    # Add pid and thread name in log file
    file_formater = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] [PID]%(process)s::%(threadName)s (%(pathname)s)  %(message)s'
    )
    log_file = Path(_log_path).expanduser().absolute().resolve()

    file_handler = TimedRotatingFileHandler(log_file, backupCount=1, encoding='utf-8', when='midnight')
    file_handler.setFormatter(file_formater)
    return file_handler


def init(config, log_queue = None):
    global LOGGER_INITED
    if LOGGER_INITED:
        return
    
    if not config:
        config = {}
    
    if not log_queue:
        log_queue = Queue()

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

    def __init__(self):
        super().__init__()
        self.queue = Queue()

    def run(self, msg_queue, config, log_queue, *args, **kwargs):
        global log_process_lock
        if not log_process_lock.acquire(timeout=10):
            return
        
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
        while True:
            try:
                log = log_queue.get()
                logger = logging.getLogger(log.name)
                logger.handle(log)
            except KeyboardInterrupt:
                log_process_lock.release()
                break        


def get_logger():
    return logging.getLogger('lyrebird')
