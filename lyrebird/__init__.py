from .manager import main, run
from .mock import context
from .mock.plugin_manager import PluginView, caller_info
from .mock.handlers.handler_context import HandlerContext
from .mock.reporter.report_handler import report
from .mock import plugin_manager
from blinker import Signal
import os
from .event import CustomEventReceiver
from lyrebird import application
from lyrebird.log import get_logger


APPLICATION_CONF_DIR = os.path.join(os.path.expanduser('~'), '.lyrebird')


event  = CustomEventReceiver()


def start_background_task(target, *args, **kwargs):
    """Start a background task in a new thread

    :param target: task function
    :param args: args will be pass to the task function
    :param kwargs: kwargs will be pass to the task function
    :return: null
    """
    context.application.socket_io.start_background_task(target, *args, **kwargs)


def emit(event, *args, **kwargs):
    """
    Send socketio event

    """
    context.application.socket_io.emit(event, *args, **kwargs)


def get_plugin_storage():
    """
    Get plugins storage dir path

    :return: ~/.lyrebird/plugins/<plugin_name>
    """
    info = caller_info(index=2)
    storage_name = info.top_module_name
    plugin_storage_dir = os.path.abspath(os.path.join(APPLICATION_CONF_DIR, 'plugins/%s' % storage_name))
    if not os.path.exists(plugin_storage_dir):
        os.makedirs(plugin_storage_dir)
    return plugin_storage_dir


def subscribe(channel, func, *args, **kwargs):
    """
    订阅信号

    :param signal: 信号，包含lyrebird, overbridge, android, tracking, perf, hunter
    :param func: 响应事件的回调函数
    :param sender: 信号发送者标识
    """
    # context.application.event_bus.subscribe(channel, func)
    application.server['event'].subscribe(channel, func, *args, **kwargs)


def publish(channel, event, *args, **kwargs):
    """
    发送信号

    :param signal: 信号，包含lyrebird, overbridge, android, tracking, perf, hunter
    :param sender: 信号发送者标识
    :param kwargs: 事件数据
    :return:
    """
    # context.application.event_bus.publish(channel, event)
    application.server['event'].publish(channel, event, *args, **kwargs)


def add_background_task(name, func):
    """
    添加后台任务

    """
    application.server['task'].add_task(name, func)


def get_plugin_conf():
    info = caller_info(index=2)
    plugin_name = info.top_module_name
    return plugin_manager.get_conf(plugin_name)


"""
获取 Event server state
"""
class StateProxy:

    def get(self, index):
        return application.server['event'].state.get(index)

    def __getitem__(self, index):
        return application.server['event'].state[index]

state = StateProxy()
