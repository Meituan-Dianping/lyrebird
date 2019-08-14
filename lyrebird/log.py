import logging
from colorama import Fore, Style, Back
from collections import namedtuple
from lyrebird import application


_stream_logger_inited = False


def get_logger()->logging.Logger:
    global _stream_logger_inited
    if not _stream_logger_inited:
        _init_stream_logger()
        _stream_logger_inited = True
    return logging.getLogger('lyrebird')


Color = namedtuple('Color', ['fore', 'style', 'back'])

COLORS = dict(
    CRITICAL=Color(fore=Fore.WHITE, style=Style.BRIGHT, back=Back.RED),
    ERROR=Color(fore=Fore.RED, style=Style.NORMAL, back=Back.RESET),
    WARNING=Color(fore=Fore.YELLOW, style=Style.NORMAL, back=Back.RESET),
    INFO=Color(fore=Fore.WHITE, style=Style.NORMAL, back=Back.RESET),
    DEBUG=Color(fore=Fore.GREEN, style=Style.NORMAL, back=Back.RESET)
)

def colorit(message, levelname):
    color = COLORS.get(levelname)
    if color:
        return f'{color.fore}{color.style}{color.back}{message}{Style.RESET_ALL}'
    else:
        return message


class ColorFormater(logging.Formatter):

    def format(self, record:logging.LogRecord):
        module = f'{colorit(record.module, record.levelname)}'
        msg = f'{colorit(record.msg, record.levelname)}'
        levelname = f'{colorit(record.levelname, record.levelname)}'
        return f'{levelname} [{module}] {msg}'


def _init_stream_logger():
    logger:logging.Logger = logging.getLogger('lyrebird')

    color_formater = ColorFormater(fmt='%(levelname)s [%(module)s] %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(color_formater)
    logger.addHandler(stream_handler)


def _init_file_logger(custom_log_path=None):
    file_formater = logging.Formatter(
        fmt='%(asctime)s %(levelname)s [%(module)s] - %(threadName)s [PID] %(process)s - %(message)s'
    )
    if custom_log_path:
        log_file = custom_log_path
    else:
        log_file = application.root_dir()/'lyrebird.log'

    file_handler = logging.handlers.TimedRotatingFileHandler(log_file, backupCount=1, encoding='utf-8', when='midnight')
    file_handler.setFormatter(file_formater)

    logger:logging.Logger = logging.getLogger('lyrebird')
    logger.addHandler(file_handler)


def _setup_3rd_loggers():
    logger_level = logging.ERROR
    socketio = logging.getLogger('socketio')
    socketio.setLevel(logger_level)

    engineio = logging.getLogger('engineio')
    engineio.setLevel(logger_level)

    mock = logging.getLogger('mock')
    mock.setLevel(logger_level)
    mock.addHandler(logging.StreamHandler())

    werkzeug = logging.getLogger('werkzeug')
    werkzeug.setLevel(logger_level)


def init(custom_log_path=None):
    _init_file_logger(custom_log_path=custom_log_path)
    _setup_3rd_loggers()

    logger:logging.Logger = logging.getLogger('lyrebird')
    verbose = application.config.get('verbose', 0)
    if verbose == 0:
        logger.setLevel(logging.ERROR)
    elif verbose == 1:
        logger.setLevel(logging.WARNING)
    elif verbose == 2:
        logger.setLevel(logging.INFO)
    elif verbose >= 3:
        logger.setLevel(logging.DEBUG)
