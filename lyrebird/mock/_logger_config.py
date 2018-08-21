import codecs
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

    def __init__(self, verbose):
        self.init_log_dir()
        self.verbose = verbose

    def init_log_dir(self):
        """
        初始化 ~/.lyrebird/log 目录

        TODO: 该操作需要考虑是否加入 filesystem 中管理，保持时序性。
        :return:
        """
        self.LOGFILE_PATH.mkdir(parents=True, exist_ok=True)

    def get_level(self):
        """
        启动参数带 v， 则 level 为 DEBUG
        启动参数不带 v，则 level 为 INFO

        :return: "DEBUG" or "INFO"
        """
        return "DEBUG" if self.verbose else "INFO"

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
        # Update handler_stream - Level from start params <v>
        set_logger_config(default_conf, logger_section='handler_stream', logger_options='level', logger_value=self.get_level())
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
        # Update handler_stream - Level from start params <v>
        set_logger_config(conf, logger_section='handler_stream', logger_options='level', logger_value=self.get_level())
        with codecs.open(self.USER_LOGGING_CONFIG, 'w', 'utf-8') as f:
            conf.write(f)

    def get_user_logging_config(self):
        self.init_logger_config()
        return self.USER_ROOT / self.LOGGING_CONFIG

    def use_default_logging_config(self):
        self.create_logger_config()
        return self.USER_ROOT / self.LOGGING_CONFIG
