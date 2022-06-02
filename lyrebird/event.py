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
import copy
from lyrebird.base_server import ThreadServer
from lyrebird import application
from lyrebird.mock import context
from lyrebird.log import get_logger


logger = get_logger()


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


class EventServer(ThreadServer):

    def __init__(self):
        super().__init__()
        self.event_queue = Queue()
        self.state = {}
        self.pubsub_channels = {}
        # channel name is 'any'. Linstening on all channel
        self.any_channel = []
        self.broadcast_executor = ThreadPoolExecutor(thread_name_prefix='event-broadcast-')

    def broadcast_handler(self, callback_fn, event, args, kwargs):
        """

        """

        # Check
        func_sig = inspect.signature(callback_fn)
        func_parameters = list(func_sig.parameters.values())
        if len(func_parameters) < 1 or func_parameters[0].default != inspect._empty:
            logger.error(f'Event callback function [{callback_fn.__name__}] need a argument for receiving event object')
            return

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
        # Execute callback function
        try:
            callback_fn(*callback_args, **callback_kwargs)
        except Exception:
            logger.error(f'Event callback function [{callback_fn.__name__}] error. {traceback.format_exc()}')

    def run(self):
        while self.running:
            try:
                e = self.event_queue.get()
                # Deep copy event for async event system
                e = copy.deepcopy(e)
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
        self.publish('system', {'name': 'event.stop'})

    def _check_message_format(self, message):
        """
        Check if the message content is valid.
        Such as: 'message' value must be a string.
        Other check rules can be added.
        """
        # Check value type of key 'message'
        message_value = message.get('message', 'No message')
        if not isinstance(message_value, str):
            raise InvalidMessage('Value of key "message" must be a string.')

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
        # Make event id
        event_id = str(uuid.uuid4())

        # Make sure event is dict
        if not isinstance(message, dict):
            # Plugins send a array list as message, then set this message to raw property
            _msg = {'raw': message}
            message = _msg
        
        self._check_message_format(message)

        message['channel'] = channel
        message['id'] = event_id
        message['timestamp'] = round(time.time(), 3)

        # Add event sender
        stack = inspect.stack()
        script_path = stack[2].filename
        script_name = script_path[script_path.rfind('/') + 1:]
        function_name = stack[2].function
        sender_dict = {
            "file": script_name,
            "function": function_name
        }
        message['sender'] = sender_dict

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
        application.reporter.report({
            'action': 'event',
            'channel': channel,
            'event': message
        })

        logger.debug(f'channel={channel} state={state}\nmessage:\n-----------\n{message}\n-----------\n')

    def subscribe(self, channel, callback_fn, *args, **kwargs):
        """
        Subscribe channel with a callback function
        That function will be called when a new message was published into it's channel

        callback function kwargs:
            channel=None receive channel name
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

    def issue(self, title, message):
        notice = {
            "title": title,
            "message": message
        }
        application.server['event'].publish('notice', notice)
