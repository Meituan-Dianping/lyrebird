from queue import Queue
from lyrebird.base_server import ThreadServer
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import traceback
from lyrebird import application
from lyrebird.log import get_logger


logger = get_logger()


class Task:
    READY = 0
    RUNNING = 1
    FINISH = 2
    ERROR = 3

    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.status = Task.READY

    def run(self):
        self.status = Task.RUNNING
        try:
            self.func()
            self.status = Task.FINISH
        except Exception:
            self.status = Task.ERROR
            logger.error(f'Exec task catch a exception:\n {traceback.format_exc()}')


class BackgroundTaskServer(ThreadServer):

    def __init__(self):
        super().__init__()
        self.tasks = []
        self.cmds = application.sync_manager.get_queue()
        self.executor = ThreadPoolExecutor(thread_name_prefix='bg-')

    def run(self):
        while self.running:
            cmd = self.cmds.get()
            if cmd is None or cmd == 'stop':
                break
            elif cmd == 'clear':
                dead_tasks = []
                for task in self.tasks:
                    if task.status == Task.FINISH or task.status == Task.ERROR:
                        dead_tasks.append(task)
                for dead_task in dead_tasks:
                    self.tasks.remove(dead_task)

    def add_task(self, name, func):
        task = Task(name, func)
        self.tasks.append(task)
        self.executor.submit(task.run)
        self.clear()

    def stop(self):
        super().stop()
        self.cmds.put('stop')

    def clear(self):
        self.cmds.put('clear')
