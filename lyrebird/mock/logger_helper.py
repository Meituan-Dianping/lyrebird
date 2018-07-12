import logging
import colorama
import copy
from logging.config import fileConfig
from .logger_config import loggingConfig

def _print_error(msg):
    print('\n!!!!!!!!!!!!!!!!!!!!!!!!\n!!!    %s\n!!!!!!!!!!!!!!!!!!!!!!!!\n' % msg)


LOG_COLORS = {
    logging.ERROR: [
        colorama.Fore.RED,
        colorama.Style.BRIGHT,
        colorama.Back.RESET
    ],
    logging.WARNING: [
        colorama.Fore.YELLOW,
        colorama.Style.NORMAL,
        colorama.Back.RESET
    ],
    logging.INFO: [
        colorama.Fore.WHITE,
        colorama.Style.NORMAL,
        colorama.Back.RESET,
    ],
    logging.CRITICAL: [
        colorama.Fore.WHITE,
        colorama.Style.BRIGHT,
        colorama.Back.RED,
    ],
    logging.DEBUG: [
        colorama.Fore.GREEN,
        colorama.Style.NORMAL,
        colorama.Back.RESET
    ]
}


def init_logger_settings():
    logging.config.fileConfig(loggingConfig.get_user_logging_config(),
                              disable_existing_loggers=False)

    socketio = logging.getLogger('socketio')
    socketio.setLevel(logging.ERROR)
    socketio.disabled = True

    engineio = logging.getLogger('engineio')
    engineio.setLevel(logging.ERROR)
    engineio.disabled = True

    mock = logging.getLogger('mock')
    mock.setLevel(logging.DEBUG)
    mock.addHandler(logging.StreamHandler())
    mock.disabled = True

    werkzeug = logging.getLogger('werkzeug')
    werkzeug.setLevel(logging.ERROR)
    werkzeug.disabled = True


class ColorFormatter(logging.Formatter):
    def format(self, record, *args, **kwargs):
        new_record = copy.copy(record)
        new_record.levelname = "{fore}{style}{back}{level}{end}".format(
            level=new_record.levelname,
            fore=LOG_COLORS[new_record.levelno][0],
            style=LOG_COLORS[new_record.levelno][1],
            back=LOG_COLORS[new_record.levelno][2],
            end=colorama.Style.RESET_ALL,
        )

        new_record.module = "{fore}{style}{module}{end}".format(
            module=new_record.module,
            fore=colorama.Fore.WHITE,
            style=colorama.Style.BRIGHT,
            end=colorama.Style.RESET_ALL
        )

        new_record.msg = "{fore}{style}{back}{msg}{end}".format(
            msg=new_record.msg,
            fore=LOG_COLORS[new_record.levelno][0],
            style=LOG_COLORS[new_record.levelno][1],
            back=LOG_COLORS[new_record.levelno][2],
            end=colorama.Style.RESET_ALL
        )

        return super(ColorFormatter, self).format(new_record)


def get_logger():
    """
    获取 logger 对象用于打印日志信息。
    e.g 获取 logger 对象
    _logger = get_logger()

    e.g 输出日志信息
    _logger.info('要输出的INFO日志信息')
    _logger.debug('要输出的DEBUG日志信息')

    :return: logger 对象
    """
    logger = logging.getLogger()
    return logger
