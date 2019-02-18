import pkg_resources
from lyrebird.mock import handlers
from collections import OrderedDict, namedtuple
import traceback
from jinja2 import Environment, PackageLoader
from flask import send_from_directory
import sys
import os
import inspect
import codecs
import json
from types import FunctionType
from pathlib import Path
from lyrebird.mock import context
from lyrebird import log
from flask import Blueprint
from .plugin_view import PluginView


"""
Plugin manager
"""

logger = log.get_logger()


ROOT_DIR = Path('~/.lyrebird').expanduser()
PLUGINS_DIR = ROOT_DIR/'plugins'


DATA_HANDLER_ENTRY_POINT = 'lyrebird_data_handler'
WEB_ENTRY_POINT = 'lyrebird_web'

# v1.0 plugin entry point
PLUGIN_ENTRY_POINT = 'lyrebird_plugin'

inner_handler = OrderedDict()
data_handler_plugins = OrderedDict()
web_plugins = OrderedDict()

# Store all plugins with project name
# Contains v1.0 plugins and older plugins
plugins = {}

# plugin blueprint list for add rule
plugin_blueprint_list = []


def _ep_to_plugin(ep, **kwargs):
    plugin = dict(
        name=ep.name, 
        version=ep.dist.version, 
        project_name=ep.dist.project_name, 
        **kwargs)
    plugin_key = plugin['project_name']
    target_plugin = plugins.get(plugin_key)
    if target_plugin:
        target_plugin.update(plugin)
    else:
        plugins[plugin_key] = plugin


def _plugin_entry_check(ep_entry):
    pass


def _load_plugin():
    for ep in pkg_resources.iter_entry_points(PLUGIN_ENTRY_POINT):
        plugin_entry = ep.load()
        if not _plugin_entry_check(plugin_entry).result:
            logger.error(f'Load plugin {plugin_entry.name} error . skip')
            continue
        

def _load_data_handler_plugin():
    data_handler_plugins.clear()
    for ep in pkg_resources.iter_entry_points(DATA_HANDLER_ENTRY_POINT):
        try:
            handler_class = ep.load()
            if not isinstance(handler_class, type):
                logger.error(f'Load plugin {ep} error. Entry point is not a class')
                continue
            if not hasattr(handler_class, 'handle'):
                logger.error(f'Load plugin {ep} error. Not found function - "handle"')
                continue
            handler = handler_class()
            data_handler_plugins[ep.name] = handler
            # Add plugin handler to new plugin object
            _ep_to_plugin(ep, beta_handler=handler)
        except Exception:
            logger.error(f'Load plugin {ep} error')
            traceback.print_exc()


def _load_web_plugin():
    web_plugins.clear()
    for ep in pkg_resources.iter_entry_points(WEB_ENTRY_POINT):
        try:
            web_class = ep.load()
        except Exception:
            logger.error(f'Load plugin fail. {ep}')
            traceback.print_exc()
            continue
        if not isinstance(web_class, type):
            logger.error(f'Load plugin {ep} error. Entry point is not a class')
            continue
        web_plugin = web_class()
        if ep.name in web_plugins:
            logger.error(f'Plugin {ep} duplicate name with {web_plugins[ep.name]}')
            continue
        if not hasattr(web_class, 'on_create'):
            logger.error(f'Load plugin {ep} error. Not found function - "on_create"')
            continue
        if not hasattr(web_class, 'index'):
            logger.error(f'Load plugin {ep} error. Not found function - "index"')
            continue
        try:
            web_plugin.on_create()
            web_plugin.after_on_create()
        except Exception:
            logger.error(f'Plugin {ep} on create', traceback.format_exc())
            continue
        web_plugins[ep.name] = web_plugin
        # Add web plugin to new plugin object
        _ep_to_plugin(ep, beta_web=web_plugin)

def _load_inner_plugin():
    inner_handler.update(handlers.get_inner_handlers())


def load():
    _load_inner_plugin()
    _load_data_handler_plugin()
    _load_web_plugin()


def add_plugin_to_blueprint(plugin, blueprint):
    """
    NEW add rule to blueprint
    """
    if not plugin:
        return
    try:
        for rule in plugin.rules:
            # 去掉自定义路由前面的"/"
            if rule.rule.startswith('/'):
                rule.rule = rule.rule[1:]
            # 为了防止重名，拼接endpoint
            if not rule.endpoint:
                rule.endpoint = plugin.name + '_' + rule.view_func.__name__
            # 注册API
            blueprint.add_url_rule(f'/{rule.rule}', rule.endpoint, view_func=rule.view_func, **rule.options)
    except Exception:
        logger.error(f'Can not add rule {rule}')
        traceback.print_exc()


def add_view_to_blueprint(blueprint):
    if len(web_plugins) == 0:
        return
    for plugin_name in web_plugins:
        plugin = web_plugins[plugin_name]
        try:
            for rule in plugin.rules:
                # 去掉自定义路由前面的"/"
                if rule.rule.startswith('/'):
                    rule.rule = rule.rule[1:]
                # 为了防止重名，拼接endpoint
                if not rule.endpoint:
                    rule.endpoint = plugin_name + '_' + rule.view_func.__name__
                # 注册视图
                blueprint.add_url_rule(
                    f'/plugin/{plugin_name}/{rule.rule}',
                    rule.endpoint,
                    view_func=rule.view_func,
                    **rule.options
                )
        except Exception:
            logger.error(f'Can not add rule {rule}')
            traceback.print_exc()


def add_event_rules(socket_io):
    if len(web_plugins) == 0:
        return
    for plugin_name in web_plugins:
        plugin = web_plugins[plugin_name]
        try:
            for event_rule in plugin.event_rules:
                socket_io.on_event(event_rule.event, event_rule.handler, event_rule.namespace)
        except Exception:
            logger.error(f'Can not add event rule {event_rule}')
            traceback.print_exc()


def caller_info(index=1):
    stack = inspect.stack()
    caller_module = inspect.getmodule(stack[index].frame)
    caller_module_name = caller_module.__name__
    if caller_module_name.find('.') > 0:
        caller_top_module_name = caller_module_name.split('.')[0]
    else:
        caller_top_module_name = caller_module_name
    CallerInfo = namedtuple('CallerInfo', 'top_module_name module_name')
    return CallerInfo(module_name=caller_module_name, top_module_name=caller_top_module_name)


class PluginNotFoundError(Exception):
    pass


def _get_plugin_conf_path(name):
    plugin = web_plugins.get(name)
    if not plugin:
        raise PluginNotFoundError('Plugin %s not fonud' % name)
    if '.' in plugin.__module__:
        top_module_name = plugin.__module__.split('.')[0]
    else:
        top_module_name = plugin.__module__
    plugin_storage_dir = PLUGINS_DIR/top_module_name
    if not plugin_storage_dir.exists():
        plugin_storage_dir.mkdir()
    return plugin_storage_dir/'conf.json'


def get_conf(name):
    conf_path = _get_plugin_conf_path(name)
    if not conf_path.exists():
        set_default_conf(name)
    with codecs.open(conf_path, 'r', 'utf-8') as f:
        return json.load(f)


def set_conf(name, conf):
    conf_path = _get_plugin_conf_path(name)
    if not conf_path.exists():
        conf_path.touch()
    with codecs.open(conf_path, 'w', 'utf-8') as f:
        f.write(json.dumps(conf, ensure_ascii=False, indent=4))
    context.application.event_bus.publish('config', dict(name=name, action='update'))


def set_default_conf(name):
    plugin = web_plugins[name]
    set_conf(name, plugin.default_conf())
    context.application.event_bus.publish('config', dict(name=name, action='update'))
