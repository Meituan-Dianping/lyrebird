"""
Base threading server class
"""

import inspect
from threading import Thread
from multiprocessing import Process
from lyrebird import application


def check_process_server_run_function_compatibility(function):
    # Check whether the run method is an old or new version by params.
    if len(inspect.signature(function).parameters) == 4 and list(inspect.signature(function).parameters.keys())[0] == 'async_obj':
        return True
    else:
        return False


service_msg_queue = None


class ProcessServer:
    def __init__(self):
        self.server_process = None
        self.running = False
        self.name = None
        self.event_thread = None
        self.async_obj = {}
        self.args = []
        self.kwargs = {}

    def run(self, async_obj, config, *args, **kwargs):
        '''
        async_obj is a dict 
        used to pass in all objects used for synchronization/communication between multiple processes
        Usually msg_queue, config and log_queue is included
            msg_queue:
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

            config:
                lyrebird config dict

            log_queue:
                send log msg to logger process
        '''
        pass

    def start(self):
        if self.running:
            return
        
        from lyrebird.log import get_logger
        logger = get_logger()

        global service_msg_queue
        if service_msg_queue is None:
            service_msg_queue = application.sync_manager.get_multiprocessing_queue()
        config = application._cm.config
        logger_queue = application.server['log'].queue

        # run method has too many arguments. Merge the msg_queue, log_queue and so on into async_obj
        # This code is used for compatibility with older versions of the run method in the plugin
        # This code should be removed after all upgrades have been confirmed
        if check_process_server_run_function_compatibility(self.run):
            self.async_obj['logger_queue'] = logger_queue
            self.async_obj['msg_queue'] = service_msg_queue
            self.server_process = Process(group=None, target=self.run,
                                        args=[self.async_obj, config, self.args],
                                        kwargs=self.kwargs,
                                        daemon=True)
        else:
            logger.warning(f'The run method in {type(self).__name__} is an old parameter format that will be removed in the future')
            self.server_process = Process(group=None, target=self.run,
                                        args=[service_msg_queue, config, logger_queue, self.args],
                                        kwargs=self.kwargs,
                                        daemon=True)
        self.server_process.start()
        self.running = True

    def stop(self):
        self.running = False
    
    def terminate(self):
        if self.server_process:
            self.server_process.terminate()
            self.server_process.join()
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
    
    def terminate(self):
        pass

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

    def terminate(self):
        pass


class MultiProcessServerMessageDispatcher(ThreadServer):

    def run(self):
        global service_msg_queue
        if service_msg_queue is None:
            service_msg_queue = application.sync_manager.get_multiprocessing_queue()
        emit = application.server['mock'].socket_io.emit
        publish = application.server['event'].publish

        while self.running:
            msg = service_msg_queue.get()
            if msg is None:
                break
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
