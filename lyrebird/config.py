from pathlib import Path
import codecs
import json
from packaging import version
from urllib.parse import urlparse
import requests
import subprocess
import time
import shutil
import jinja2
import json
import os
from lyrebird import log as nlog


logger = nlog.get_logger()


config_template = {
    "version": "0.10.5",
    "proxy.filters": [],
    "proxy.port": 4272,
    "mock.port": 9090,
    "mock.data": "{{current_dir}}/mock_data/personal",
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
        loaded_config = json.loads(template.render(current_dir=str(self.config_root), download_dir=str(self.ROOT/'downloads')))
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


resource_template = {
    'uri': None,
    'config': None
}


class Rescource:
    cache_filename = 'resource.json'
    download_dirname = 'downloads'

    def __init__(self, conf_root_path='~/.lyrebird'):
        self.root = Path(conf_root_path).expanduser().absolute()
        self.cache_file = self.root / self.cache_filename
        self.download_dir = self.root / self.download_dirname
        self.cache = None
        # load cache
        self.load()

    def load(self):
        if self.cache_file.exists():
            with codecs.open(self.cache_file, 'r', 'utf-8') as f:
                try:
                    self.cache = json.load(f)
                except Exception:
                    self.cache = resource_template
        else:
            self.cache = resource_template

    def save(self):
        with codecs.open(self.cache_file, 'w', 'utf-8') as f:
            f.write(json.dumps(self.cache, ensure_ascii=False, indent=4))
            f.close()

    def download(self, uri):
        self.cache['uri'] = uri
        self.save()

        if self.download_dir.exists():
            shutil.rmtree(self.download_dir.absolute())
        self.download_dir.mkdir(exist_ok=True)

        uri = urlparse(self.cache.get('uri'))
        if uri.scheme == 'http' or uri.scheme == 'https':
            self._http()
        elif uri.scheme.startswith('git+'):
            self._git()
        else:
            raise RescourceException(f'Unknown scheme {self.cache}')

    def _git(self):
        git_url = self.cache.get('uri')[4:]
        p = subprocess.run(f'git clone {git_url} {self.download_dir.absolute()}', shell=True)
        p.check_returncode()
        logger.warning(f'Source downloaded to {str(self.download_dir.absolute())}')

    def _http(self):
        # resp = requests.get(self.cache.get('uri'), allow_redirects=True)
        # TODO support http download
        # 1. download gzip file and unzip it
        # 2. download from git repo
        pass


class RescourceException(Exception):
    pass
