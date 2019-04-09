from queue import Queue
from lyrebird.base_server import ThreadServer
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import traceback
from lyrebird import application



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
            result = self.func()
            self.status = Task.FINISH
            application.server['event'].publish('task',
            {
                'status': 'finish',
                'code': '1000',
                'result': result
            })
        except Exception:
            self.status = Task.ERROR
            application.server['event'].publish('task',
            {
                'status': 'error',
                'code': '3000',
                'message': traceback.format_exc()
            })


class BackgroundTaskServer(ThreadServer):

    def __init__(self):
        super().__init__()
        self.tasks = []
        self.cmds = Queue()
        self.executor = ThreadPoolExecutor(thread_name_prefix='bg-')

    def run(self):
        while self.running:
            cmd = self.cmds.get()
            if cmd == 'stop':
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
