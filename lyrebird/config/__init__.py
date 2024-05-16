import json
import codecs
import jinja2
from os import path
from pathlib import Path
from copy import deepcopy
from packaging import version
from lyrebird import log as nlog
from lyrebird import application

from lyrebird.utils import RedisDict
from lyrebird.config.diff_mode import SettingDiffMode
from lyrebird.config.checker_switch import SettingCheckerSwitch

from .keywords import *

logger = nlog.get_logger()

config_template = {
    "version": "0.10.5",
    "proxy.filters": [],
    "proxy.port": 4272,
    "mock.port": 9090,
    "mock.data": path.join("{{current_dir}}", "mock_data", "personal"),
    "mock.proxy_headers": {
        "scheme": "MKScheme",
        "host": "MKOriginHost",
        "port": "MKOriginPort"
    }
}

CONFIG_FUNC_MAP = {
    'checker.switch': SettingCheckerSwitch,
    'mock.mode': SettingDiffMode
}

personal_config_template = {
    "event.broken_database_path_list": []
}


class ConfigManager():
    ROOT = Path('~/.lyrebird').expanduser()
    DEFAULT_FILENAME = 'conf.json'
    DEFAULT_PERSONAL_FILENAME = 'personal_conf.json'
    BASE_CONFIG = ROOT / DEFAULT_FILENAME
    PERSONAL_CONFIG = ROOT / DEFAULT_PERSONAL_FILENAME
    FORBIDDEN_MODIFY_FIELDS_IN_CONFIG = set(['version', 'proxy.port', 'mock.port'])

    def __init__(self, conf_path_list=None, custom_conf=None):
        self.config = config_template
        self.config_root = self.ROOT
        self.conf_file = self.BASE_CONFIG
        self.config_list = []
        # Current personal config only supports checking whether lyrebird.db is broken.
        self.personal_config = personal_config_template
        self.personal_conf_file = self.PERSONAL_CONFIG

        self.update_base_config()
        self.read_config()
        if conf_path_list:
            for conf_path in conf_path_list:
                self.update_conf_source(conf_path)
        if custom_conf:
            self.update_conf_custom(custom_conf)

        if self.config.get('enable_multiprocess', False):
            try:
                self.config = RedisDict(data=self.config,
                                        host=self.config.get('redis_host', '127.0.0.1'),
                                        port=self.config.get('redis_port', 6379),
                                        db=self.config.get('redis_db', 0))
            except Exception as e:
                self.config['enable_multiprocess'] = False
                logger.error(f'Start enable multiprocess failed, Redis connection error:\n{e}')

        self.initialize_personal_config()

    def update_conf_source(self, path):
        input_path: Path = Path(path).expanduser().absolute()
        if input_path.is_dir():
            input_root = input_path
            input_file = input_path / self.DEFAULT_FILENAME
        else:
            input_root = input_path.parent
            input_file = input_path

        if not input_file.exists():
            logger.error(f'Config {input_file} not found!')
        else:
            self.config_root = input_root
            self.conf_file = input_file
            self.read_config()

    def update_conf_custom(self, custom_conf):
        self.add_config(custom_conf, rank=-1)

    def contains_forbidden_modify_field(self, update_conf: dict):
        union_fields = self.FORBIDDEN_MODIFY_FIELDS_IN_CONFIG & update_conf.keys()
        return union_fields if len(union_fields) > 0 else None

    def override_config_field(self, update_conf: dict):
        """
        Update Application config by ``config.update(update_conf)``.
        If update_conf contains ``FORBIDDEN_MODIFY_FIELDS_IN_CONFIG``, raise ``ConfigException``.
        """
        if not update_conf:
            return

        forbidden_modify_fields = self.contains_forbidden_modify_field(update_conf)
        if forbidden_modify_fields:
            raise ConfigException(f'Config field cannot be modified: {forbidden_modify_fields}')

        update_level = self.config.get('config.update_config.level', 1)

        logger.debug(f'Need update config fields: {update_conf}')
        self.add_config(update_conf, type='api_patch', level=update_level, apply_now=True)
        logger.debug(f'Update done. config: {self.config}')

        application.server['event'].publish('config_update', {'config_update' : {'data': str(update_conf)}})

    def read_config(self):
        template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(self.config_root)))
        template = template_env.get_template(self.conf_file.name)
        current_dir = str(self.config_root)
        download_dir = str(self.ROOT / 'downloads')
        conf_str = template.render(current_dir=json.dumps(current_dir).strip('"'), download_dir=json.dumps(download_dir).strip('"'))
        loaded_config = json.loads(conf_str)

        self.add_config(loaded_config, rank=-10)

    def write_config(self):
        self.config_root.mkdir(parents=True, exist_ok=True)
        with codecs.open(self.conf_file, 'w', 'utf-8') as f:
            f.write(json.dumps(self.config, indent=4, ensure_ascii=False))

    def update_base_config(self):
        if self.BASE_CONFIG.exists() and self.BASE_CONFIG.is_file():
            with codecs.open(self.BASE_CONFIG, 'r', 'utf-8') as f:
                base_conf = json.load(f)
                if version.parse(base_conf.get('version', '0.0.0')) < version.parse(config_template.get('version', '0.0.0')):
                    self.write_config()
        else:
            self.write_config()

    def add_config(self, config_dict: dict, rank=0, type='', override_same_type=False, level=1, apply_now=False) -> None:
        config = Config(config_dict, level, self.config)
        config.type = type

        if override_same_type:
            for c in self.config_list[::-1]:
                if c.type == type:
                    self.config_list.remove(c)
        self.config_list.append(config)

        self.merge_config(self.config, config.config, level=level, apply_now=apply_now)

    def merge_config(self, origin_config, new_config, level=-1, apply_now=False):
        for key_child in list(new_config.keys()):
            self.merge_generator(key_child, origin_config, new_config, level)

        if apply_now:
            self.add_each_config_item(new_config)

    def merge_generator(self, key, origin_config, new_config, level):
        if level == 0:
            return

        if key not in origin_config:
            origin_config[key] = deepcopy(new_config[key])

        elif origin_config[key] == new_config[key]:
            return

        elif level == 1:
            origin_config[key] = deepcopy(new_config[key])

        elif type(origin_config[key]) != type(new_config[key]):
            origin_config[key] = deepcopy(new_config[key])

        elif isinstance(new_config[key], list):
            origin_config[key] = deepcopy(new_config[key])

        elif isinstance(new_config[key], dict):
            for key_child in list(new_config[key].keys()):
                self.merge_generator(key_child, origin_config[key], new_config[key], level-1)

        else:
            origin_config[key] = new_config[key]

    def add_each_config_item(self, config):
        # 处理第一层的key
        for key, value in config.items():
            if key not in CONFIG_FUNC_MAP:
                continue
            CONFIG_FUNC_MAP[key].add(value)

    def remove_config(self, config=None, type='', apply_now=False):
        remove_config = None
        for c in self.config_list[::-1]:
            if c.type == type and (config is None or config == c.config):
                remove_config = c
                break

        if remove_config is None:
            logger.error("No matching config found in config_list.")
            return

        self.unmerge_config(self.config, remove_config.config, level=remove_config.level, apply_now=apply_now)

        self.merge_config(self.config, remove_config.previous_config, level=remove_config.level, apply_now=apply_now)

        # todo handle the config added after remove_config

        self.config_list.remove(remove_config)

    def unmerge_config(self, origin_config, remove_config, level=-1, apply_now=False):
        for key_child in list(remove_config.keys()):
            self.unmerge_generator(key_child, origin_config, remove_config, level=level)

        if apply_now:
            self.remove_each_config_item(remove_config)

    def unmerge_generator(self, key, origin_config, remove_config, level):
        if level == 0:
            return

        if key not in origin_config:
            return

        if level == 1:
            origin_config.pop(key, None)

        elif isinstance(remove_config[key], dict):
            for key_child in list(remove_config[key].keys()):
                self.unmerge_generator(key_child, origin_config[key], remove_config[key], level-1)

        else:
            origin_config.pop(key, None)

    def remove_each_config_item(self, config):
        # 处理第一层的key
        for key, value in config.items():
            if key not in CONFIG_FUNC_MAP:
                continue
            CONFIG_FUNC_MAP[key].remove(value)
    
    def initialize_personal_config(self):
        if not self.personal_conf_file.exists():
            self.write_personal_config()
        self.personal_config = self.read_personal_config()
    
    def update_personal_config(self, config_dict: dict):
        self.personal_config = config_dict
        self.write_personal_config()

    def read_personal_config(self):
        try:
            with codecs.open(self.personal_conf_file, 'r', 'utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f'Failed to parse personal config file {self.personal_conf_file}!')
            return personal_config_template

    def write_personal_config(self):
        try:
            with codecs.open(self.personal_conf_file, 'w', 'utf-8') as f:
                f.write(json.dumps(self.personal_config, indent=4, ensure_ascii=False))
        except Exception as e:
            logger.error(f'Failed to write personal config: {e}')


class Config:
    def __init__(self, config, level=1, current_config={}):
        self.rank = 0
        self.type = ''
        self.config = config
        self.level = level
        self.previous_config = self._get_previuos_config(current_config, level)

    def _get_previuos_config(self, current_config, level):
        if not current_config:
            return {}
        previous_config = {}
        for key in self.config.keys():
            self._get_previous_config_generator(key, self.config, current_config, previous_config, level)
        return previous_config
    
    def _get_previous_config_generator(self, key, config, current_config, previous_config, level):
        if not current_config or key not in current_config:
           return

        if level != 1 and isinstance(config[key], dict):
            previous_config[key] = {}
            for key_child in config[key].keys():
                self._get_previous_config_generator(key_child, config[key], current_config.get(key), previous_config[key], level-1)
        else:
            previous_config[key] = deepcopy(current_config.get(key))


class ConfigException(Exception):
    pass
