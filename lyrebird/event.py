"""
Event bus

Worked as a backgrund thread
Run events handler and background task worker
"""
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import traceback
import inspect
import uuid
import time
from lyrebird.base_server import ThreadServer
from lyrebird import application
from lyrebird.mock import context
from lyrebird.log import get_logger


logger = get_logger()


class Event:
    """
    Event bus inner class
    """
    def __init__(self, channel, message):
        self.channel = channel 
        self.message = message


class EventServer(ThreadServer):
    
    def __init__(self):
        super().__init__()
        self.event_queue = Queue()
        self.state = {}
        self.pubsub_channels = {}
        # channel name is 'any'. For linstening all channel's message
        self.any_channel = []
        self.broadcast_executor = ThreadPoolExecutor(thread_name_prefix='event-broadcast-')
        # display notice in frontend
        self.subscribe('alert', self.display_notice)

    def broadcast_handler(self, callback_fn, event, args, kwargs):
        try:
            if kwargs.get('event', False):
                callback_fn(event)
            else:
                callback_fn(event.message)
        except Exception:
            # TODO handle exceptioins and send to event bus
            traceback.print_exc()

    def run(self):
        while self.running:
            try:
                e = self.event_queue.get()
                callback_fn_list = self.pubsub_channels.get(e.channel)
                if callback_fn_list:
                    for callback_fn, args, kwargs in callback_fn_list:
                        self.broadcast_executor.submit(self.broadcast_handler, callback_fn, e, args, kwargs)
                for callback_fn, args, kwargs in self.any_channel:
                    self.broadcast_executor.submit(self.broadcast_handler, callback_fn, e, args, kwargs)
            except Exception:
                # empty event
                traceback.print_exc()

    def stop(self):
        super().stop()
        self.publish('any', 'stop')

    def publish(self, channel, message, state=False, *args, **kwargs):
        """
        publish message

        if type of message is dict, set default event information: 
            - channel
            - id
            - timestamp
            - sender: if was cantained in message, do not update

        if state is true, message will be kept as state

        """
        if isinstance(message, dict):
            message['channel'] = channel
            message['id'] = str(uuid.uuid4())
            message['timestamp'] = int(time.time())
            if not message.get('sender'):
                stack = inspect.stack()
                script_path = stack[2].filename
                script_name = script_path[script_path.rfind('/') + 1:]
                function_name = stack[2].function
                sender_dict = {
                    "file": script_name,
                    "function": function_name
                }
                message['sender'] = sender_dict
        
        self.event_queue.put(Event(channel, message))
        if state:
            self.state[channel] = message
        logger.debug(f'channel={channel} state={state}\nmessage:\n-----------\n{message}\n-----------\n')

    def subscribe(self, channel, callback_fn, *args, **kwargs):
        """
        Subscribe channel with a callback function
        That function will be called when a new message was published into it's channel

        kwargs:
            event=False receiver gets a message dict
            event=True receiver gets an Event object
        """
        if channel == 'any':
            self.any_channel.append([callback_fn, args, kwargs])
        else:
            callback_fn_list = self.pubsub_channels.setdefault(channel, [])
            callback_fn_list.append([callback_fn, args, kwargs])


    def unsubscribe(self, channel, target_callback_fn, *args, **kwargs):
        """
        Unsubscribe callback function from channel
        """
        if channel == 'any':
            for any_channel_fn, *_ in self.any_channel:
                if target_callback_fn == any_channel_fn:
                    self.any_channel.remove([target_callback_fn, *_])
        else:
            callback_fn_list = self.pubsub_channels.get(channel)
            for callback_fn, *_ in callback_fn_list:
                if target_callback_fn == callback_fn:
                    callback_fn_list.remove([target_callback_fn, *_])

    def display_notice(self, msg):
        """
        display notice
        
        """
        context.application.socket_io.emit('show', msg, namespace='/alert')

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
            event_bus.subscribe(listener['channel'], listener['func'])

    def unregister(self, event_bus):
        for listener in self.listeners:
            event_bus.unsubscribe(listener['channel'], listener['func'])

    def publish(self, channel, message, *args, **kwargs):
        application.server['event'].publish(channel, message, *args, **kwargs)

    def alert(self, channel, message, *args, **kwargs):
        stack = inspect.stack()
        script_name = stack[1].filename
        script_name = script_name[script_name.rfind('/') + 1:]
        function_name = stack[1].function
        if isinstance(message, dict):
            message['script_name'] = script_name
            message['function_name'] = function_name
        application.server['event'].publish(channel, message, *args, **kwargs)

    def issue(self, message, issue_message=None, channel="issue"):
        notice = {"message": message,
                    "actions": [
                        {
                            "type": "carrier",
                            "box": {
                                "channel": channel,
                                'message': issue_message,
                                "state": True
                            }
                        }
                    ]}
        application.server['event'].publish('notice', notice)
