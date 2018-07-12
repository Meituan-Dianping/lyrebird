import os, codecs, shutil
import configparser
from pathlib import Path


not_set_section = ['loggers', 'handlers', 'formatters', 'logger_root']


def set_logger_config(conf, *, logger_section, logger_options, logger_value):
    if logger_section in not_set_section:
        return
    if not conf.has_section(logger_section):
        conf.add_section(logger_section)
    conf.set(logger_section, logger_options, logger_value)


class LoggingConfig:

    USER_ROOT = Path('~', '.lyrebird').expanduser()
    CURRENT_PATH = Path(__file__).resolve().parent
    LOGGER_TMP_CONFIG = CURRENT_PATH / '../templates' / 'logging_config.ini'
    LOGFILE_PATH = USER_ROOT / 'log'
    LOGGING_CONFIG = 'logging_config.ini'
    USER_LOGGING_CONFIG = USER_ROOT / LOGGING_CONFIG

    def __init__(self):
        self.init_log_dir()
        self.init_logger_config()

    def init_log_dir(self):
        """
        初始化 ~/.lyrebird/log 目录

        TODO: 该操作需要考虑是否加入 filesystem 中管理，保持时序性。
        :return:
        """
        self.LOGFILE_PATH.mkdir(parents=True, exist_ok=True)

    def init_logger_config(self):
        if self.USER_LOGGING_CONFIG.exists():
            self.update_logger_config()
        else:
            self.create_logger_config()

    def update_logger_config(self):
        user_conf = configparser.RawConfigParser()
        user_conf.read(self.USER_LOGGING_CONFIG)
        default_conf = configparser.RawConfigParser()
        default_conf.read(self.LOGGER_TMP_CONFIG)
        for section in user_conf.sections():
            for option in user_conf.options(section):
                set_logger_config(
                    conf=default_conf,
                    logger_section=section,
                    logger_options=option,
                    logger_value=user_conf.get(section, option)
                )
        with codecs.open(self.USER_LOGGING_CONFIG, 'w', 'utf-8') as f:
            default_conf.write(f)

    def create_logger_config(self):
        conf = configparser.RawConfigParser()
        conf.read(self.LOGGER_TMP_CONFIG)
        set_logger_config(
            conf,
            logger_section='handler_logFileHandler',
            logger_options='args',
            logger_value='("%s", "midnight", 1, 5, "utf-8")' % (self.USER_ROOT / 'log' / 'lyrebird.log')
        )
        with codecs.open(self.USER_LOGGING_CONFIG, 'w', 'utf-8') as f:
            conf.write(f)

    def get_user_logging_config(self):
        return self.USER_ROOT / self.LOGGING_CONFIG


loggingConfig = LoggingConfig()