from jinja2 import Environment, PackageLoader
from flask import send_from_directory
import sys
import os
import inspect
import codecs


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
