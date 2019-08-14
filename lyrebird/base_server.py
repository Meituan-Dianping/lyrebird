"""
Base threading server class
"""

from threading import Thread


class ThreadServer:

    def __init__(self):
        self.server_thread = None
        self.running = False

    def start(self, *args, **kwargs):
        if self.running:
            return
        self.running = True
        self.server_thread = Thread(target=self.run, args=args, kwargs=kwargs)
        self.server_thread.start()

    def stop(self):
        self.running = False

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
