"""
Event bus

Worked as a backgrund thread
Run events handler and background task worker
"""
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import traceback

import sys

from lyrebird.base_server import ThreadServer
from lyrebird.mock import context
import inspect


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
        self.broadcast_executor = ThreadPoolExecutor(max_workers=10, thread_name_prefix='event-broadcast')

    def broadcast_handler(self, callback_fn, message):
        try:
            callback_fn(message)
        except Exception:
            # TODO handle exceptioins and send to event bus
            traceback.print_exc()

    def run(self):
        while self.running:
            try:
                e = self.event_queue.get()
                callback_fn_list = self.pubsub_channels.get(e.channel)
                if callback_fn_list:
                    for callback_fn in callback_fn_list:
                        self.broadcast_executor.submit(self.broadcast_handler, callback_fn, e.message)
                for callback_fn in self.any_channel:
                    self.broadcast_executor.submit(self.broadcast_handler, callback_fn, e.message)
            except Exception:
                # empty event
                traceback.print_exc()

    def stop(self):
        super().stop()
        self.publish('any', 'stop')

    def publish(self, channel, message, state=False, *args, **kwargs):
        """
        publish message
        if state is true, message will be keep as state

        """
        self.event_queue.put(Event(channel, message))
        if state:
            self.state[channel] = message


    def subscribe(self, channel, callback_fn, *args, **kwargs):
        """
        Subscribe channel with a callback function
        That function will be called when a new message was published into it's channel
        """
        if channel == 'any':
            self.any_channel.append(callback_fn)
        else:
            callback_fn_list = self.pubsub_channels.setdefault(channel, [])
            callback_fn_list.append(callback_fn)


    def unsubscribe(self, channel, callback_fn, *args, **kwargs):
        """
        Unsubscribe callback function from channel
        """
        if channel == 'any' and callback_fn in self.any_channel:
            self.any_channel.remove(callback_fn)
        else:
            callback_fn_list = self.pubsub_channels.get(channel)
            if callback_fn_list and callback_fn in callback_fn_list:
                callback_fn_list.remove(callback_fn)


class CustomEventReceiver:
    """
    Event Receiver

    Decorator for plugin developer
    useaeg:
        event = CustomEventReceiver()

        @event('flow')
        def on_message(data):
            pass
    """
    def __init__(self):
        self.listeners = []
        self.caller_file = ''
        self.caller_method = ''

    def __call__(self, channel, object=False, *args, **kw):
        def func(origin_func):
            self.listeners.append(dict(channel=channel, func=origin_func, object=object))
            self.caller_file = sys.argv[0]
            self.caller_method = origin_func.__name__
            return origin_func
        return func

    def register(self, event_bus):
        for listener in self.listeners:
            event_bus.subscribe(listener['channel'], listener['func'])

    def unregister(self, event_bus):
        for listener in self.listeners:
            event_bus.unsubscribe(listener['channel'], listener['func'])

    def publish(self, channel, message, *args, **kwargs):
        context.application.event_bus.publish(channel, message, *args, **kwargs)

    def alert(self, channel, message, *args, **kwargs):
        caller_file = self.caller_file[self.caller_file.rfind('/') + 1:]
        if isinstance(message, dict):
            message['caller_file'] = caller_file
            message['caller_method'] = self.caller_method
        context.application.event_bus.publish(channel, message, *args, **kwargs)
    