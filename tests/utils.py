class FakeSocketio:

    def emit(self, event, *args, **kwargs): 
        print(f'Send event {event} args={args} kw={kwargs}')
 
    def run(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass


class FakeEvnetServer:
    
    def run(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

    def terminate(self, *args, **kwargs):
        pass

    def publish(self, *args, **kwargs):
        pass

    def subscribe(self, *args, **kwargs):
        pass

    def unsubscribe(self, *args, **kwargs):
        pass

class FakeReportor:

    def run(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

    def terminate(self, *args, **kwargs):
        pass

    def report(self, *args, **kwargs):
        pass

class FakeBackgroundTaskServer:

    def run(self, *args, **kwargs):
        pass

    def stop(self, *args, **kwargs):
        pass

    def terminate(self, *args, **kwargs):
        pass

    def add_task(self, *args, **kwargs):
        pass
