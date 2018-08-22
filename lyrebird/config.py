from pathlib import Path
import codecs
import json
from packaging import version
from urllib.parse import urlparse
import requests
import subprocess
import time
import shutil
from lyrebird import log as nlog


logger = nlog.get_logger()


config_template = {
  "version": "0.10.5",
  "proxy.filters": [],
  "proxy.port": 4272,
  "mock.port": 9090,
  "mock.data": "data",
  "mock.proxy_headers": {
    "scheme": "MKScheme",
    "host": "MKOriginHost",
    "port": "MKOriginPort"
  }
}


class ConfigManager():
    default_conf_filename = 'conf.json'

    def __init__(self, conf_root_path='~/.lyrebird'):
        self.root = None
        self.config = None
        self.conf_file = None
        self.update_conf(conf_root_path)

    def update_conf(self, path):
        input_path:Path = Path(path).expanduser().absolute()
        if input_path.is_dir():
            self.root = input_path
            self.conf_file = input_path / self.default_conf_filename
        else:
            self.root = input_path.parent
            self.conf_file = input_path

        # load config or use default config
        if self.conf_file.exists():
            self.read()
            # check if need upgrade config
            if version.parse(config_template.get('version', '0.0.0')) > version.parse(self.config.get('version', '0.0.0')):
                self.config = config_template
                self.save()
        else:
            self.root.mkdir(parents=True, exist_ok=True)
            self.config = config_template
            self.save()

    def read(self):
        with codecs.open(self.conf_file, 'r', 'utf-8') as f:
            self.config = json.load(f)

    def save(self):
        with codecs.open(self.conf_file, 'w', 'utf-8') as f:
            f.write(json.dumps(self.config, ensure_ascii=False, indent=4))


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
        resp = requests.get(self.cache.get('uri'), allow_redirects=True)
        # TODO support http download 
        # 1. download gzip file and unzip it
        # 2. download from git repo


class RescourceException(Exception):
    pass
