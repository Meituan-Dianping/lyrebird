from pathlib import Path
from os import path
import codecs
import json
from packaging import version
import jinja2
from lyrebird import log as nlog


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


class ConfigManager():
    ROOT = Path('~/.lyrebird').expanduser()
    DEFAULT_FILENAME = 'conf.json'
    BASE_CONFIG = ROOT/DEFAULT_FILENAME

    def __init__(self, conf_path=None):
        self.config = config_template
        self.config_root = self.ROOT
        self.conf_file = self.BASE_CONFIG

        self.update_base_config()
        self.read_config()
        if conf_path:
            self.update_conf_source(conf_path)

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

    def read_config(self):
        template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(self.config_root)))
        template = template_env.get_template(self.conf_file.name)
        current_dir = str(self.config_root)
        download_dir = str(self.ROOT/'downloads')
        conf_str = template.render(current_dir=json.dumps(current_dir).strip('"'), download_dir=json.dumps(download_dir).strip('"'))
        loaded_config = json.loads(conf_str)
        self.config.update(loaded_config)

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


class ConfigException(Exception):
    pass
