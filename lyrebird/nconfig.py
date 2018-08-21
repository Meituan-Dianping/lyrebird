from pathlib import Path
import codecs
import json
from packaging import version
from urllib.parse import urlparse
import requests
import subprocess
import time
import shutil


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
    conf_filename = 'conf.json'

    def __init__(self, conf_root_path='~/.lyrebird'):
        self.config = None
        self.conf_root_path = conf_root_path
        self.root = Path(conf_root_path).expanduser()

    @property
    def conf_root_path(self):
        return self._conf_root_path

    @conf_root_path.setter
    def conf_root_path(self, value):
        self._conf_root_path = value
        self.conf_path = Path(self._conf_root_path).expanduser() / self.conf_filename
        self.create_config()

    def create_config(self):
        # load config or use default config
        if self.conf_path.exists():
            self.read()
            # check if need upgrade config
            if version.parse(config_template.get('version', '0.0.0')) > version.parse(self.config.get('version', '0.0.0')):
                self.config = config_template
                self.save()
        else:
            self.config = config_template
            self.save()

    def read(self):
        with codecs.open(self.conf_path, 'r', 'utf-8') as f:
            self.config = json.load(f)

    def save(self):
        with codecs.open(self.conf_path, 'w', 'utf-8') as f:
            f.write(json.dumps(self.config, ensure_ascii=False, indent=4))
            f.close()


resource_template = {
    'uri': None,
    'lastUpdate': None
}

class Rescource:
    cache_filename = 'resource.json'
    download_dirname = 'downloads'

    def __init__(self, conf_root_path='~/.lyrebird'):
        self._uri = None
        self.cache_file = Path(conf_root_path).expanduser() / self.cache_filename
        self.download_dir = Path(conf_root_path).expanduser() / self.download_dirname

    @property
    def uri(self):
        return self._uri.geturl()

    @uri.setter
    def uri(self, value):
        self._uri = urlparse(value)

    def load(self):
        if self.cache_file.exists():
            with codecs.open(self.cache_file, 'r', 'utf-8') as f:
                cache = json.load(f)
                self.uri = cache.get('uri')

    def save(self):
        with codecs.open(self.cache_file, 'w', 'utf-8') as f:
            resource_template['uri'] = self.uri
            resource_template['lastUpdate'] = time.time()
            f.write(json.dumps(resource_template, ensure_ascii=False, indent=4))
            f.close()

    def download(self):
        if self.download_dir.exists():
            shutil.rmtree(self.download_dir.absolute())
        self.download_dir.mkdir(exist_ok=True)

        if self._uri.scheme == 'http' or self._uri.scheme == 'https':
            self._http()
        elif self._uri.scheme == 'file' or self._uri.scheme == '':
            self._local()
        elif self._uri.scheme.startswith('git+'):
            self._git()
        else:
            raise RescourceException(f'Unknown scheme {self.uri}')
        
    def _git(self):
        git_url = self.uri[4:]
        p = subprocess.run(f'git clone {git_url} {self.download_dir.absolute()}', shell=True)
        p.check_returncode()
    
    def _http(self):
        resp = requests.get(self.uri)
        print(resp, self.download_dir)

    def _local(self):
        file_path = self._uri.path


class RescourceException(Exception):
    pass