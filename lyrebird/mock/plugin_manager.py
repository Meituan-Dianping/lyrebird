import pkg_resources
from . import handlers
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
from . import context
from lyrebird import log
from flask import Blueprint

"""
Plugin manager
"""

logger = log.get_logger()


ROOT_DIR = Path('~/.lyrebird').expanduser()
PLUGINS_DIR = ROOT_DIR/'plugins'


DATA_HANDLER_ENTRY_POINT = 'lyrebird_data_handler'
WEB_ENTRY_POINT = 'lyrebird_web'

# new EP
PLUGIN_ENTRY_POINT = 'lyrebird_plugin'

inner_handler = OrderedDict()
data_handler_plugins = OrderedDict()
web_plugins = OrderedDict()

"""
Plugin
"""
plugins = OrderedDict()

# plugin blueprint list for add rule
plugin_blueprint_list = []


class Rule:
    """
    视图路由规则

    """

    def __init__(self, rule, endpotion, view_func=None, **options):
        self.rule = rule
        self.endpoint = endpotion
        self.view_func = view_func
        self.options = options

    def __str__(self):
        return f'Rule {self.rule} func={self.view_func}'


class EventRule:
    """
    socket-io事件规则
    """

    def __init__(self, event, handler, namespace):
        self.event = event
        self.handler = handler
        self.namespace = namespace

    def __str__(self):
        return f'Event rule {self.event} handler={self.handler}'


class Plugin:
    """
    NEW 插件基类

    """

    def __init__(self):
        self.static_folder = None
        self.static_uri = None
        self.static_path = None
        self.rules = []
        self.event_rules = []
        self.option = None
        self.version = None
        self.name = None
        self.key = None

    def keys(self):
        '''
        当对实例化对象使用dict(obj)的时候, 会调用这个方法,这里定义了字典的键, 其对应的值将以obj['name']的形式取,
        但是对象是不可以以这种方式取值的, 为了支持这种取值, 可以为类增加一个方法
        '''
        return ('static_uri', 'option', 'static_folder', 'version', 'name', 'key')

    def __getitem__(self, item):
        '''
        内置方法, 当使用obj['name']的形式的时候, 将调用这个方法, 这里返回的结果就是值
        '''
        return getattr(self, item)

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        self.rules.append(Rule(rule, endpoint, view_func, **options))

    def on_event(self, event, handler, namespace):
        self.event_rules.append(EventRule(event, handler, namespace))

    def on_create(self):
        """
        初始生命周期
        通过在该函数内调用'add_url_rule'添加处理请求的路由，插件的主页面要使用'/'路径
        """
        pass

    def after_on_create(self):
        if not self.static_folder:
            self.set_static_root()

    def set_static_root(self, package_name=None, static_path='static'):
        self.static_path = static_path
        if not package_name:
            package_name = self._get_current_package_name()
        target_module = sys.modules.get(package_name)
        package_path = os.path.dirname(target_module.__file__)
        self.static_folder = os.path.abspath(os.path.join(package_path, static_path))

    def _get_current_package_name(self):
        """
        通过class判断包名
        :return: 
        """
        module_name = self.__class__.__module__
        if '.' in module_name:
            return module_name.split('.')[0]
        return module_name


class PluginView:
    """
    插件视图基类

    """

    def __init__(self):
        self.env = Environment()
        self.rules = []
        self.event_rules = []
        self.static_folder = None
        self.template_folder = None

    def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
        self.rules.append(Rule(rule, endpoint, view_func, **options))

    def on_event(self, event, handler, namespace):
        self.event_rules.append(EventRule(event, handler, namespace))

    def on_create(self):
        """
        初始生命周期
        通过在该函数内调用'set_template_root'指定前端模板目录
        通过在该函数内调用'set_static_root'指定前端静态文件目录
        通过在该函数内调用'add_url_rule'添加处理请求的路由，插件的主页面要使用'/'路径
        """
        pass

    def after_on_create(self):
        if not self.static_folder:
            self.set_static_root()
        if not self.template_folder:
            self.set_template_root()

    def _get_current_package_name(self):
        """
        通过class判断包名
        :return: 
        """
        module_name = self.__class__.__module__
        if '.' in module_name:
            return module_name.split('.')[0]
        return module_name

    def get_package_file_path(self, file_path, package_name=None):
        if not package_name:
            package_name = self._get_current_package_name()
        target_module = sys.modules.get(package_name)
        package_path = os.path.dirname(inspect.getsourcefile(target_module))
        return os.path.abspath(os.path.join(package_path, file_path))

    def set_template_root(self, package_name=None, templates_path='templates'):
        """
        设置html模板根目录. 默认在 [插件包]/templates 下

        :param package_name: 包名，不指定时默认读取当前插件包 
        :param templates_path: 模板路径， 默认为templates目录
        """
        if not package_name:
            package_name = self._get_current_package_name()
        self.env.loader = PackageLoader(package_name, package_path=templates_path)
        target_module = sys.modules.get(package_name)
        package_path = os.path.dirname(target_module.__file__)
        self.template_folder = os.path.abspath(os.path.join(package_path, templates_path))

    def set_static_root(self, package_name=None, static_path='static'):
        """
        设置静态文件(css、js等)目录. 默认在 [插件包]/static 下

        :param package_name: 包名，不指定时默认读取当前插件包 
        :param static_path: 静态文件目录， 默认为static目录
        """
        if not package_name:
            package_name = self._get_current_package_name()
        target_module = sys.modules.get(package_name)
        package_path = os.path.dirname(target_module.__file__)
        self.static_folder = os.path.abspath(os.path.join(package_path, static_path))
        self.add_url_rule('/static/<path:filename>', view_func=self.send_static_file)

    def render_template(self, template, *args, **kwargs):
        """
        渲染模板，支持jinja2语法

        :param template: 模板文件名 
        :param args: 参数数组
        :param kwargs: 参数字典
        :return: 返回渲染完成的html文本
        """
        return self.env.get_template(template).render(*args, **kwargs)

    def send_static_file(self, filename):
        """
        响应静态文件
        收到请求后，按照filename在静态文件目录下查找，并返回静态文件

        :param filename: 
        :return: 
        """
        # todo cache_timeout
        return send_from_directory(self.static_folder, filename)

    def send_template_file(self, filename):
        template_file_path = os.path.abspath(os.path.join(self.template_folder, filename))
        return codecs.open(template_file_path, 'r', 'utf-8').read()

    def default_conf(self):
        """
        设置默认的 conf.json

        :return: 返回 conf.json 内容
        """
        # todo plugin conf 应该以对象方式读取存储 并且对外只读，特定方法支持写
        return {}


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
        except Exception:
            logger.error(f'Load plugin {ep} error')
            traceback.print_exc()


def get_change_response_plugins():
    need_change_resp_handlers = []
    for plugin in data_handler_plugins.items():
        if hasattr(plugin, 'change_response'):
            if isinstance(plugin.change_response, bool) and plugin.change_response:
                need_change_resp_handlers.append(plugin)
            elif isinstance(plugin.change_response, FunctionType) and plugin.change_response():
                need_change_resp_handlers.append(plugin)
    return need_change_resp_handlers


def _check_data_handlers_response_conflict():
    need_change_resp_handlers = get_change_response_plugins()
    if len(need_change_resp_handlers) > 1:
        logger.error(
            f'More than one plugin will modify response. Please check those plugins {need_change_resp_handlers}')


def _load_plugins():
    """
    NEW load plugin
    """
    plugins.clear()
    for ep in pkg_resources.iter_entry_points(PLUGIN_ENTRY_POINT):
        try:
            plugin_class = ep.load()
        except Exception:
            logger.error(f'Load plugin fail. {ep}')
            traceback.print_exc()
            continue
        if not isinstance(plugin_class, type(Plugin)):
            logger.error(f'Load plugin {ep} error. Entry point is not a class')
            continue
        plugin = plugin_class()
        if ep.name in plugins:
            logger.error(f'Plugin {ep} duplicate name with {plugins[ep.name]}')
            continue
        try:
            plugin.on_create()
            plugin.after_on_create()
            plugin.name = ep.name
            plugin.version = ep.dist.version
            plugin.key = ep.dist.key
            # 注册蓝图
            plugin_blueprint = Blueprint(str(plugin.key),
                                         __name__, url_prefix=f'/plugin/{plugin.name}',
                                         static_folder=plugin.static_folder)
            plugin.static_uri = '/plugin/' + plugin.name + '/' + plugin.static_path + '/'
            add_plugin_to_blueprint(plugin, plugin_blueprint)
            plugin_blueprint_list.append(plugin_blueprint)
        except Exception:
            logger.error(f'Plugin {ep} on create', traceback.format_exc())
            continue
        plugins[ep.name] = plugin


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


def _load_inner_plugin():
    inner_handler.update(handlers.get_inner_handlers())


def load():
    _load_inner_plugin()
    _load_data_handler_plugin()
    _check_data_handlers_response_conflict()
    _load_web_plugin()
    # new add load plugins function
    _load_plugins()


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
