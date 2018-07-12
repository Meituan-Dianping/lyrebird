import codecs
import json
import os
from pathlib import Path
import shutil
from packaging import version

from lyrebird.mock.logger_helper import get_logger
from .version import IVERSION
from typing import List
from flask import Response, abort
from lyrebird.mock.console_helper import warning_msg, err_msg
import subprocess

"""
Config manager

Config file path: ~/.lyrebird/conf.json
Lyrebird will copy config template to ~/.lyrebird/conf.json, when lyrebird server start. 
"""

CURRENT_DIR = Path(__file__).parent

CONFIG_TEMPLATE_FILE = CURRENT_DIR/'templates'/'conf.json'
CACHE_TEMPLATE_FILE = CURRENT_DIR/'templates'/'cache.json'


class Config:

    def __init__(self, root_dir='~', name='lyrebird'):
        self.root = Path(root_dir, '.lyrebird').expanduser()
        self.default_conf_path = Path(self.root, 'conf.json').expanduser()
        self.custom_conf_dir = Path(self.root, 'conf').expanduser()
        self.cache_path = Path(self.root, 'cache.json').expanduser()
        self.pid_path = Path(self.root, f'{name}.pid').expanduser()
        self.tmp_dir = Path(self.root, 'tmp').expanduser()
        self.plugin_root = Path(self.root, 'plugins')

    def init(self):
        if not self.root.exists():
            self.root.mkdir()
        if not self.default_conf_path.exists():
            shutil.copyfile(CONFIG_TEMPLATE_FILE, self.default_conf_path)
        else:
            current_conf_version = self.load_default().get('version', '0.0.0')
            template_conf_version = self.load_template().get('version', '0.0.0')
            if version.parse(current_conf_version) < version.parse(template_conf_version):
                shutil.copyfile(CONFIG_TEMPLATE_FILE, self.default_conf_path)
        if not self.cache_path.exists():
            shutil.copyfile(CACHE_TEMPLATE_FILE, self.cache_path)
        if not self.custom_conf_dir.exists():
            self.custom_conf_dir.mkdir(parents=True)
        if not self.tmp_dir.exists():
            self.tmp_dir.mkdir(parents=True)

    def load(self, name):
        conf = self.load_default()
        if name:
            conf.update(self.load_custom(name))
        else:
            self.load_cache().get('custom_conf')
        return conf

    def load_template(self):
        return json.loads(codecs.open(CONFIG_TEMPLATE_FILE).read())

    def load_default(self):
        return json.loads(codecs.open(self.default_conf_path).read())

    def load_custom(self, name):
        if not name.endswith('.json'):
            name = name + '.json'
        custom_conf_path = self.custom_conf_dir / name
        if custom_conf_path.exists():
            return json.loads(codecs.open(self.custom_conf_dir/name).read())
        else:
            return json.loads(codecs.open(self.custom_conf_dir/'tmp.json').read())

    def save_pid(self):
        with codecs.open(self.pid_path, 'w', 'utf-8') as f:
            f.write(str(os.getpid()))

    def read_pid(self):
        with codecs.open(self.pid_path, 'r', 'utf-8') as f:
            return int(f.read())

    def remove_pid(self):
        if self.pid_path.exists():
            os.remove(self.pid_path)

    def load_tmp(self, name, **kwargs):
        tmp_conf_path = self.custom_conf_dir/'tmp.json'
        with codecs.open(tmp_conf_path, 'w', 'utf-8') as f:
            f.write(json.dumps(kwargs, indent=4, ensure_ascii=False))
        conf = self.load(name)
        conf.update(kwargs)
        return conf

    def load_cache(self):
        if self.cache_path.exists():
            with codecs.open(self.cache_path, 'r', 'utf-8') as f:
                return json.loads(f.read())
        else:
            raise ConfCacheNotFound

    def save_cache(self, cache):
        with codecs.open(self.cache_path, 'w', 'utf-8') as f:
            f.write(json.dumps(cache, indent=4, ensure_ascii=False))

    def download(self, uri):
        repo = self.tmp_dir/'repo'
        if repo.exists():
            shutil.rmtree(repo)
        p = subprocess.run(f"git clone {uri} {repo}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode == 0:
            print(p.stdout.decode())
        else:
            # raise GitCloneFailed(p.stderr.decode())
            get_logger().critical(
                msg=f'下载配置文件错误,但不影响Overbridge使用,可以手动import相应插件base \n download conf data by git failed:{p.stderr.decode()}')
            return
        for subfile in repo.iterdir():
            if not subfile.is_dir():
                continue
            if subfile.name.startswith('.'):
                continue
            if subfile.name == 'conf':
                for conf_file in subfile.iterdir():
                    shutil.copy(conf_file, self.custom_conf_dir/conf_file.name)
            else:
                try:
                    dst = os.path.join(self.plugin_root, subfile.name)
                    command = f'cp -f -R {subfile}/* {dst}'
                    if not os.path.exists(dst):
                        os.makedirs(dst)
                    subprocess.run(command, shell=True)
                except Exception as e:
                    print(e)


class ConfCacheNotFound(Exception):
    pass


class GitCloneFailed(Exception):
    pass
