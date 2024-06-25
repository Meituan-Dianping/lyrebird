"""
Event bus

Worked as a backgrund thread
Run events handler and background task worker
"""
import os
import imp
import sys
import copy
import uuid
import time
import copy
import types
import signal
import pickle
import inspect
import importlib
import functools
import traceback
import setuptools
from concurrent.futures import ThreadPoolExecutor
from lyrebird.base_server import ThreadServer, ProcessServer
from lyrebird.compatibility import prepare_application_for_monkey_patch, monkey_patch_application, monkey_patch_issue, monkey_patch_publish
from lyrebird import application
from lyrebird.mock import context
from lyrebird import log
from pathlib import Path


logger = log.get_logger()
# only report the checker which duration more the 5s
LYREBIRD_METRICS_REPORT_DURSTION = 5000


class InvalidMessage(Exception):
    pass


class Event:
    """
    Event bus inner class
    """

    def __init__(self, event_id, channel, message):
        self.id = event_id
        self.channel = channel
        self.message = message

    def __getstate__(self):
        return pickle.dumps({
            'event_id':self.id,
            'channel':self.channel,
            'message':self.message
            })

    def __setstate__(self, state):
        data = pickle.loads(state)
        self.id = data['event_id']
        self.channel = data['channel']
        self.message = data['message']


def import_func_module(path):
    path = os.path.dirname(path)
    packages = setuptools.find_packages(path)
    for pkg in packages:
        manifest_file = Path(path)/pkg/'manifest.py'
        if not manifest_file.exists():
            continue
        if pkg in sys.modules:
            continue
        sys.path.append(str(Path(path)/pkg))
        imp.load_package(pkg, Path(path)/pkg)


def import_func_from_file(filepath, func_name):
    name = os.path.basename(filepath)[:-3]
    if name in sys.modules:
        module = sys.modules[name]
    else:
        # 从文件加载模块
        spec = importlib.util.spec_from_file_location(name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[name] = module
    return getattr(module, func_name)


def get_func_from_obj(obj, method_name):
    return getattr(obj, method_name)


def get_callback_func(func_ori, func_name):
    if isinstance(func_ori, str):
        return import_func_from_file(func_ori, func_name)
    elif isinstance(func_ori, object):
        return get_func_from_obj(func_ori, func_name)
    else:
        logger.error(f'The source type of method {func_name} is invalid, exception method source: {func_ori}')


def callback_func_run_statistic(callback_fn, args, kwargs, report_info):
    from lyrebird import application
    event_start_time = time.time()
    callback_fn(*args, **kwargs)
    event_end_time = time.time()
    event_duration = (event_end_time - event_start_time) * 1000
    # Report the operation of Event
    # Prevent loop reporting, and only long time event(more than 5s) are reported
    if event_duration < LYREBIRD_METRICS_REPORT_DURSTION:
        return
    if report_info['channel'] == 'lyrebird_metrics':
        return
    if not application.config.get('event.lyrebird_metrics_report', True):
        return
    application.server['event'].publish('lyrebird_metrics', {'lyrebird_metrics': {
        'sender': 'EventServer',
        'action': 'broadcast_handler',
        'duration': event_duration,
        'trace_info': str(report_info['trace_info'])
    }})


class CustomExecuteServer(ProcessServer):
    def __init__(self):
        super().__init__()
        self.event_thread_executor = None
    
    def run(self, async_obj, config, *args, **kwargs):
        self.event_thread_executor = ThreadPoolExecutor(max_workers=async_obj['max_thread_workers'])

        signal.signal(signal.SIGINT, signal.SIG_IGN)

        for _, path in async_obj['plugins']:
            import_func_module(path)

        log_queue = async_obj['logger_queue']
        process_queue = async_obj['process_queue']
        publish_queue = async_obj['publish_queue']

        # monkey_patch is performed on the context content of the process to ensure 
        # that functions of Lyrebird can still be used in the process.

        async_funcs = {}
        async_funcs['publish'] = functools.partial(monkey_patch_publish, publish_queue=publish_queue)
        async_funcs['issue'] = functools.partial(monkey_patch_issue, publish_queue=publish_queue)
        monkey_patch_application(async_obj, async_funcs)

        log.init(config, log_queue)
        self.running = True
        
        while self.running:
            try:
                msg = process_queue.get()
                if not msg:
                    break
                func_ori, func_name, callback_args, callback_kwargs, info = msg
                callback_fn = get_callback_func(func_ori, func_name)
                self.event_thread_executor.submit(callback_func_run_statistic, callback_fn, callback_args, callback_kwargs, info)
            except Exception:
                traceback.print_exc()

    def start(self):
        plugins = application.server['plugin'].plugins
        plugins = [(p_name, plugin.location) for p_name, plugin in plugins.items()]
        self.async_obj['plugins'] = plugins
        self.async_obj['max_thread_workers'] = application.config.get('event.multiprocess.thread_max_worker', 1)
        super().start()


class PublishServer(ThreadServer):
    def __init__(self):
        super().__init__()
        self.publish_msg_queue = application.sync_manager.get_multiprocessing_queue()

    def run(self):
        while self.running:
            try:
                msg = self.publish_msg_queue.get()
                if not msg:
                    break
                event_id, channel, message, args, kwargs = msg
                application.server['event'].publish(channel, message, event_id=event_id, *args, **kwargs)
            except Exception:
                traceback.print_exc()


class EventServer(ThreadServer):

    async_starting = False
    publish_trace_deep = 3

    def __init__(self, no_start = False):
        super().__init__()  
        self.state = {}
        self.pubsub_channels = {}
        # channel name is 'any'. Linstening on all channel
        self.any_channel = []
        self.process_executor_queue = None
        self.event_queue = None
        self.broadcast_executor = None
        self.process_executor = None
        self.publish_server = None
        self.only_report_channel = None
        if not no_start:
            self.only_report_channel = application.config.get('event.only_report_channel', [])
            self.process_executor_queue = application.sync_manager.get_multiprocessing_queue()
            self.event_queue = application.sync_manager.get_queue()
            self.broadcast_executor = ThreadPoolExecutor(thread_name_prefix='event-broadcast-')
            self.process_executor = CustomExecuteServer()
            self.publish_server = PublishServer()

    def broadcast_handler(self, func_info, event, args, kwargs, process_queue=None):
        """

        """
        callback_fn = func_info.get('func')
        is_process = func_info.get('process')

        # Check
        func_sig = inspect.signature(callback_fn)
        func_parameters = list(func_sig.parameters.values())
        if len(func_parameters) < 1 or func_parameters[0].default != inspect._empty:
            logger.error(f'Event callback function [{callback_fn.__name__}] need a argument for receiving event object')
            return
        
        # get enable multiprocess channel list
        multiprocess_channel_list = application.config.get('event.multiprocess.channels', [])

        # Append event content to args
        callback_args = []
        if 'raw' in event.message:
            callback_args.append(event.message['raw'])
        else:
            callback_args.append(event.message)
        # Add channel to kwargs
        callback_kwargs = {}
        if 'channel' in func_sig.parameters:
            callback_kwargs['channel'] = event.channel
        if 'event_id' in func_sig.parameters:
            callback_kwargs['event_id'] = event.id
        # add report info
        info = dict()
        info['trace_info'] = {
            'channel': event.channel,
            'event_id': event.id,
            'callback_fn': callback_fn.__name__,
            'callback_kwargs': str(callback_kwargs)
        }
        info['channel'] = event.channel
        # Execute callback function
        try:
            if EventServer.async_starting and is_process and isinstance(callback_fn, types.FunctionType) and event.channel in multiprocess_channel_list:
                process_queue.put((
                    func_info.get('origin'),
                    func_info.get('name'),
                    callback_args,
                    callback_kwargs,
                    info
                ))
            else:
                callback_func_run_statistic(callback_fn, callback_args, callback_kwargs, info)
        except Exception:
            logger.error(f'Event callback function [{callback_fn.__name__}] error. {traceback.format_exc()}')

    def run(self):
        while self.running:
            try:
                e = self.event_queue.get()
                if not e:
                    break
                # Deep copy event for async event system
                e = copy.deepcopy(e)
                callback_fn_list = self.pubsub_channels.get(e.channel)
                if callback_fn_list:
                    for callback_fn, args, kwargs in callback_fn_list:
                        self.broadcast_executor.submit(self.broadcast_handler, callback_fn, e, args, kwargs, self.process_executor_queue)
                for callback_fn, args, kwargs in self.any_channel:
                    self.broadcast_executor.submit(self.broadcast_handler, callback_fn, e, args, kwargs)
            except Exception:
                # empty event
                traceback.print_exc()

    def async_start(self):
        if not self.publish_server.running:
            self.publish_server.start()
        self.process_namespace = prepare_application_for_monkey_patch()
        self.process_executor.async_obj['process_queue'] = self.process_executor_queue
        self.process_executor.async_obj['process_namespace'] = self.process_namespace
        self.process_executor.async_obj['publish_queue'] = self.publish_server.publish_msg_queue
        self.process_executor.async_obj['eventserver'] = EventServer
        self.process_executor.start()
        application.server['event_process_executor'] = self.process_executor
        EventServer.async_starting = True
        self.publish('system', {'system': {'action': 'event.multiprocess', 'module': 'event_server', 'status': 'READY'}})

    def stop(self):
        self.publish('system', {'name': 'event.stop'})
        time.sleep(1)
        super().stop()
        self.process_executor.stop()
        self.publish_server.stop()

    @staticmethod
    def _check_message_format(message):
        """
        Check if the message content is valid.
        Such as: 'message' value must be a string.
        Other check rules can be added.
        """
        # Check value type of key 'message'
        message_value = message.get('message', 'No message')
        if not isinstance(message_value, str):
            raise InvalidMessage('Value of key "message" must be a string.')

    @staticmethod
    def get_publish_message(channel, message, event_id=None):
        if not event_id:
            # Make event id
            event_id = str(uuid.uuid4())

            # Make sure event is dict
            if not isinstance(message, dict):
                # Plugins send a array list as message, then set this message to raw property
                _msg = {'raw': message}
                message = _msg

            EventServer._check_message_format(message)

            message['channel'] = channel
            message['id'] = event_id
            message['timestamp'] = round(time.time(), 3)

            # Add event sender
            stack = inspect.stack()
            script_path = stack[EventServer.publish_trace_deep].filename
            script_name = script_path[script_path.rfind('/') + 1:]
            function_name = stack[EventServer.publish_trace_deep].function
            sender_dict = {
                "file": script_name,
                "function": function_name
            }
            message['sender'] = sender_dict   
        return (event_id, channel, message)

    def publish(self, channel, message, state=False, event_id=None, *args, **kwargs):
        """
        publish message

        if type of message is dict, set default event information:
            - channel
            - id
            - timestamp
            - sender: if was cantained in message, do not update

        if state is true, message will be kept as state

        """
        event_id, channel, message = EventServer.get_publish_message(channel, message, event_id)

        if channel in self.pubsub_channels or channel not in self.only_report_channel:
            self.event_queue.put(Event(event_id, channel, message))

        # TODO Remove state and raw data
        if state:
            if 'raw' in message:
                self.state[channel] = message['raw']
            else:
                self.state[channel] = message

        # Send event to socket-io
        context.application.socket_io.emit('event', {'id': event_id, 'channel': channel})

        # Send report
        if application.reporter:
            application.reporter.report({
                'action': 'event',
                'channel': channel,
                'event': message
            })

        logger.debug(f'channel={channel} state={state}\nmessage:\n-----------\n{message}\n-----------\n')

    def subscribe(self, func_info, *args, **kwargs):
        """
        Subscribe channel with a callback function
        That function will be called when a new message was published into it's channel

        callback function kwargs:
            channel=None receive channel name
        """
        channel = func_info['channel']
        if 'process' not in func_info:
            func_info['process'] = True
        if channel == 'any':
            self.any_channel.append([func_info, args, kwargs])
        else:
            callback_fn_list = self.pubsub_channels.setdefault(channel, [])
            callback_fn_list.append([func_info, args, kwargs])

    def unsubscribe(self, target_func_info, *args, **kwargs):
        """
        Unsubscribe callback function from channel
        """
        channel = target_func_info['channel']
        if channel == 'any':
            for any_info, *_ in self.any_channel:
                if target_func_info['func'] == any_info['func']:
                    self.any_channel.remove([target_func_info, *_])
        else:
            callback_fn_list = self.pubsub_channels.get(channel)
            for callback_fn_info, *_ in callback_fn_list:
                if target_func_info['func'] == callback_fn_info['func']:
                    callback_fn_list.remove([target_func_info, *_])


class CustomEventReceiver:
    """
    Event Receiver

    Decorator for plugin developer
    Usage:
        event = CustomEventReceiver()

        @event('flow')
        def on_message(data):
            pass
    """

    def __init__(self):
        self.listeners = []

    def __call__(self, channel, object=False, *args, **kw):
        def func(origin_func):
            self.listeners.append(dict(channel=channel, func=origin_func, object=object))
            return origin_func
        return func

    def register(self, event_bus):
        for listener in self.listeners:
            event_bus.subscribe({
                'name': 'CustomEventReceiver',
                'channel': listener['channel'],
                'func': listener['func']
            })

    def unregister(self, event_bus):
        for listener in self.listeners:
            event_bus.unsubscribe({
                'name': 'CustomEventReceiver',
                'channel': listener['channel'],
                'func': listener['func']
            })

    def publish(self, channel, message, *args, **kwargs):
        application.server['event'].publish(channel, message, *args, **kwargs)

    def issue(self, title, message):
        notice = {
            "title": title,
            "message": f'[CustomEventReceiver]: message'
        }
        application.server['event'].publish('notice', notice)
