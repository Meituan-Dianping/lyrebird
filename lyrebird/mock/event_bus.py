from concurrent.futures import ThreadPoolExecutor
import traceback
import time
from . import context

"""
Event bus

Events:
* HTTP flow events
* Config events
* Plugin events
"""

class EventBus:
    """
    Main event bus class

    Use thread pool to execute event handle functions.
    """

    ANY = 'any'

    def __init__(self):
        self.receivers = {'any':[]}
        self.event_executor = ThreadPoolExecutor()

    def subscribe(self, channel, func, *args, **kwargs):
        channel_receivers = self.receivers.setdefault(channel, [])
        channel_receivers.append(func)

    def publish(self, channel, event, *args, **kwargs):
        if isinstance(event, dict):
            event['channel'] = channel
            event['time'] = time.time()
        channel_receivers = self.receivers.get(channel)
        if channel_receivers:
            for receiver in channel_receivers:
                self.event_executor.submit(self.receiver_wrapper, receiver, event)
        if channel != EventBus.ANY:
            for receiver in self.receivers.get(EventBus.ANY):
                self.event_executor.submit(self.receiver_wrapper, receiver, event)

    def unsubscribe(self, channel, func):
        channel_receivers = self.receivers.get(channel)
        channel_receivers.remove(func)
    
    def receiver_wrapper(self, func, event):
        try:
            func(event)
        except Exception:
            print('!!execute receiver error', traceback.format_exc())


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
        context.application.event_bus.publish(channel, message, *args, **kwargs)
    