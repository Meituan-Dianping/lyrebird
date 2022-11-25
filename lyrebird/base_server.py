"""
Base threading server class
"""

from threading import Thread
from multiprocessing import Process, Queue
from lyrebird import application

service_msg_queue = Queue()


class ProcessServer:
    def __init__(self):
        self.server_process = None
        self.running = False
        self.name = None
        self.event_thread = None
        self.args = []
        self.kwargs = {}

    def run(self, queue, config, *args, **kwargs):
        '''
        queue
        message queue for process server and main process

        #1. Send event to main process,
        {
            "type": "event",
            "channel": "",
            "content": {}
        }

        #2. Send message to frontend
        support channel: msgSuccess msgInfo msgError
        {
            "type": "ws",
            "channel": "",
            "content": ""
        }

        config
        lyrebird config dict
        '''
        pass

    def start(self):
        if self.running:
            return

        global service_msg_queue
        config = application.config.raw()
        self.server_process = Process(group=None, target=self.run,
                                      args=[service_msg_queue, config, self.args],
                                      kwargs=self.kwargs,
                                      daemon=True)
        self.server_process.start()
        self.running = True

    def stop(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None


class ThreadServer:

    def __init__(self):
        self.server_thread = None
        self.running = False
        self.name = None

    def start(self, *args, **kwargs):
        if self.running:
            return
        self.running = True
        self.server_thread = Thread(target=self.run, name=self.name, args=args, kwargs=kwargs)
        self.server_thread.start()

    def stop(self):
        self.running = False
        # TODO terminate self.server_thread

    def run(self):
        """
        Server main function
        """
        pass


class StaticServer:

    def start(self, *args, **kwargs):
        pass

    def stop(self):
        pass


class MultiProcessServerMessageDispatcher(ThreadServer):

    def run(self):
        global service_msg_queue
        emit = application.server['mock'].socket_io.emit
        publish = application.server['event'].publish

        while True:
            msg = service_msg_queue.get()
            type = msg.get('type')
            if type == 'event':
                channel = msg.get('channel')
                event = msg.get('content')
                if channel and event:
                    publish(channel, event)
            elif type == 'ws':
                ws_channel = msg.get('channel')
                ws_msg = msg.get('content', '')
                if ws_channel:
                    emit(ws_channel, ws_msg)
            else:
                pass
