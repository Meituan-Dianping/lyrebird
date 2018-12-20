import json
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import requests
from lyrebird.mock import context
import datetime
from ...version import VERSION
import subprocess
import sys
import getpass
import os
from .. import plugin_manager
from lyrebird import log


lyrebird_start_time = None
last_page = None
last_page_in_time = None


logger = log.get_logger()


class ReportHandler:
    """
    用于上报到ELK的处理器

    """

    def __init__(self):
        self.report_url = None
        self.report_headers = None
        self.event_executor = ThreadPoolExecutor(max_workers=5)

    def report_worker(self, data):
        # 如果配置文件无reporter的配置
        conf = context.application.conf
        if not conf.get('reporter.url') or not conf.get('reporter.headers'):
            return
        
        self.report_url = conf['reporter.url']
        self.report_headers = conf['reporter.headers']
        
        if isinstance(data, dict):
            data.update(base_data)
        
        try:
            requests.request("POST", self.report_url, json=data, headers=self.report_headers)
        except Exception as e:
            logger.error(f'Send report failed. \n{data} \n{e}')

    def send_report(self, data):
        self.event_executor.submit(self.report_worker, data)


report_handler = ReportHandler()


def report(data):
    report_handler.send_report(data)


def _env_info():
    user_name = subprocess.run('git config user.name', shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
    user_email = subprocess.run('git config user.email', shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
    return {
        'username': getpass.getuser(),
        'platform': sys.platform,
        'version': sys.version,
        'argv': sys.argv,
        'git.user_name': user_name, 
        'git.user_email': user_email,
        'pid': os.getpid()
        }

def _make_base_data():
        # web plugin 信息
    web_plugins = {}
    for name in plugin_manager.web_plugins:
        plugin = plugin_manager.web_plugins[name]
        web_plugins[name] = {
            'class': plugin.__class__.__name__,
            'module': plugin.__module__
        }
    # data plugin 信息
    data_plugins = {}
    for name in plugin_manager.data_handler_plugins:
        plugin = plugin_manager.data_handler_plugins[name]
        data_plugins[name] = {
            'class': plugin.__class__.__name__,
            'module': plugin.__module__
        }
    data = {
        'reporter':'lyrebird', 
        'version':VERSION, 
        'webPlugins': web_plugins,
        'dataPlugins': data_plugins, 
        'env': _env_info()
        }

    return data

    
base_data = _make_base_data()


def _make_data(action):
    data = {}
    data.update(base_data)
    data['action'] = action
    data['time'] = str(datetime.datetime.now())
    return data


def _page_out():
    global last_page
    global last_page_in_time

    if last_page and last_page_in_time:
        duration = datetime.datetime.now() - last_page_in_time
        page_out_data = _make_data('page.out')
        page_out_data['page'] = last_page
        page_out_data['duration'] = duration.total_seconds()
        report(page_out_data)


def page_in(name):
    _page_out()
    
    global last_page
    global last_page_in_time

    data = _make_data('page.in')
    data['page'] = name
    report(data)
    
    last_page = name
    last_page_in_time = datetime.datetime.now()


def start():
    global lyrebird_start_time
    lyrebird_start_time = datetime.datetime.now()
    data = _make_data('start')
    report(data)


def stop():
    _page_out()
    data = _make_data('stop')
    data['duration'] = (datetime.datetime.now() - lyrebird_start_time).total_seconds()
    report(data)