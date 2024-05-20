from .manager import main, run
from .mock import context
from .mock.dm.jsonpath import jsonpath
from .mock.handlers.handler_context import HandlerContext
import os
from .event import CustomEventReceiver
from .checker import event
from .checker import encoder, decoder
from .checker import on_request, on_response, on_request_upstream, on_response_upstream
from .plugins import get_plugin_storage
from lyrebird import application
from lyrebird.log import get_logger

APPLICATION_CONF_DIR = os.path.join(os.path.expanduser('~'), '.lyrebird')


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


def subscribe(channel, func, name='', *args, **kwargs):
    """
    订阅信号

    :param signal: 信号，包含lyrebird, overbridge, android, tracking, perf, hunter
    :param func: 响应事件的回调函数
    :param sender: 信号发送者标识
    """
    # context.application.event_bus.subscribe(channel, func)
    func_info = {
        'name': name,
        'channel': channel,
        'func': func
    }
    application.server['event'].subscribe(func_info, *args, **kwargs)


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



"""
获取 Event server state
"""


class StateProxy:

    def get(self, index):
        return application.server['event'].state.get(index)

    def __getitem__(self, index):
        return application.server['event'].state[index]


state = StateProxy()


def report(data):
    application.reporter.report(data)
