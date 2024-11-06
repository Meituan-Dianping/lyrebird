import os
import json
import shutil
import inspect
import lyrebird
import importlib
import traceback

from lyrebird import application
from lyrebird.log import get_logger
from copy import deepcopy
from types import FunctionType
from pathlib import Path
from lyrebird.base_server import StaticServer
from .settings_template import SettingsTemplate

logger = get_logger()

class Settings:

    def __init__(self, script):
        self.script = script
        self.name = f'{self.script.stem}'
        self.inited = False
        self.template = None

    def __getattr__(self, name):
        if self.template and hasattr(self.template, name):
            return getattr(self.template, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def load(self):
        try:
            module_loader = importlib.util.spec_from_file_location(self.name, self.script)
            module = importlib.util.module_from_spec(module_loader)
            module_loader.loader.exec_module(module)
        except Exception as e:
            logger.error(f'Setting item load failed, file path:{str(self.script)}\n {traceback.format_exc()} \n {e}')
        
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, SettingsTemplate) and obj != SettingsTemplate:
                try:
                    template = obj()
                    self.template = template
                    break
                except Exception as e:
                    logger.error(f'Setting item init failed, file path:{self.name}\n {traceback.format_exc()} \n {e}')
        if self.template:
            self.inited = True

    def getter(self):
        if not self.inited:
            return f'Setting item operate is blocked, because it load failed, item name:{self.name}'
        res = {}
        try:
            res = self.template.getter()
        except Exception as e:
            logger.error(f'Setting item getter failed, item name:{self.name}\n {traceback.format_exc()} \n {e}')
        finally:
            return res

    def setter(self, data):
        if not self.inited:
            return f'Setting item operate is blocked, because it load failed, item name:{self.name}'
        res = ''
        try:
            res = self.template.setter(data)
        except Exception as e:
            res = f'Setting item setter failed, item name:{self.name}\n {traceback.format_exc()} \n {e}'
            logger.error(res)
        return res

    def restore(self):
        if not self.inited:
            return f'Setting item operate is blocked, because it load failed, item name:{self.name}'
        res = ''
        try:
            res = self.template.restore()
        except Exception as e:
            res = f'Setting item restore failed, item name:{self.name}\n {traceback.format_exc()} \n {e}'
            logger.error(res)
        return res

    def load_finished(self):
        if not self.inited:
            return f'Setting item operate is blocked, because it load failed, item name:{self.name}'
        res = ''
        try:
            res = self.template.load_finished()
        except Exception as e:
            res = f'Setting item load_finished failed, item name:{self.name}\n {traceback.format_exc()} \n {e}'
            logger.error(res)
        return res

    def load_prepared(self):
        if not self.inited:
            return f'Setting item operate is blocked, because it load failed, item name:{self.name}'
        res = ''
        try:
            res = self.template.load_prepared()
        except Exception as e:
            res = f'Setting item load_prepared failed, item name:{self.name}\n {traceback.format_exc()} \n {e}'
            logger.error(res)
        return res

    def destory(self):
        if not self.inited:
            return f'Setting item operate is blocked, because it load failed, item name:{self.name}'
        try:
            self.template.destory()
        except Exception as e:
            logger.error(f'Setting item destory failed, item name:{self.name}\n {traceback.format_exc()} \n {e}')


class SettingsManager(StaticServer):

    def __init__(self):
        self.SCRIPTS_DIR_TEMPLATE = Path(lyrebird.APPLICATION_CONF_DIR)/'settings'
        self.PERSONAL_CONFIG_PATH = Path(lyrebird.APPLICATION_CONF_DIR)/'personal_conf.json'
        self.EXAMPLE_DIR = Path(__file__).parent.parent/'examples'/'settings'
        self.configs = deepcopy(application._cm.personal_config)
        self.settings = application.settings
    
    def stop(self):
        for name, setting in self.settings.items():
            setting.destory()
    
    def load_finished(self):
        for name, setting in self.settings.items():
            setting.load_finished()

    def load_prepared(self):
        for name, setting in self.settings.items():
            setting.load_prepared()

    def load_settings(self):
        scripts_list = self.get_settings_list()
        if not scripts_list:
            return

        switch_conf = application.config.get('settings.switch', [])
        for script in scripts_list:
            if script.name not in switch_conf:
                continue
            if script.inited:
                continue

            script.load()
            if script.inited:
                self.settings[script.name] = script
        
        self.load_prepared()

    def get_settings_list(self):
        workspace_str = application.config.get('settings.workspace')

        if workspace_str:
            workspace = Path(workspace_str)
            if not workspace.expanduser().exists():
                logger.error(f'Settings scripts dir {workspace_str} not found!')
                return
            workspace_iterdir = self.get_iterdir_python(workspace)
            if not workspace_iterdir:
                logger.warning(f'No settings script found in dir {workspace_str}')
                return
        else:
            workspace = Path(self.SCRIPTS_DIR_TEMPLATE)
            workspace.mkdir(parents=True, exist_ok=True)
            workspace_iterdir = self.get_iterdir_python(workspace)
            if not workspace_iterdir:
                self.copy_example_scripts()

        return workspace_iterdir

    @staticmethod
    def get_iterdir_python(path):
        path = Path(path)
        end_str = '.py'
        scripts_list = [Settings(i) for i in path.iterdir() if i.suffix == end_str]
        return scripts_list

    def copy_example_scripts(self):
        for example in self.EXAMPLE_DIR.iterdir():
            if not example.name.endswith('.py'):
                continue
            dst = self.SCRIPTS_DIR_TEMPLATE / example.name
            shutil.copy(example, dst)

    def write_config(self, obj:SettingsTemplate, data={}):
        if data and not isinstance(data, dict):
            return
        template_key = f'settings.{obj.name}'
        template = {
            template_key: self.configs.get(template_key, {})
        }
        if data:
            template[template_key].update(data)
        self.configs.update(template)
        application._cm.update_personal_config(template)

    def get_config(self, obj:SettingsTemplate):
        template_key = f'settings.{obj.name}'
        return self.configs.get(template_key, {})
