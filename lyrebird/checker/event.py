from lyrebird import application
from .. import checker


class CheckerEventHandler:

    def __call__(self, channel, *args, **kw):
        def func(origin_func):
            if not checker.scripts_tmp_storage.get(checker.TYPE_EVENT):
                checker.scripts_tmp_storage[checker.TYPE_EVENT] = []
            checker.scripts_tmp_storage[checker.TYPE_EVENT].append({
                'name': origin_func.__name__,
                'func': origin_func,
                'channel': channel
            })
            return origin_func
        return func

    def issue(self, title, message):
        notice = {
            "title": title,
            "message": message
        }
        application.server['event'].publish('notice', notice)

    def publish(self, channel, message, *args, **kwargs):
        application.server['event'].publish(channel, message, *args, **kwargs)

    @staticmethod
    def register(func_info):
        application.server['event'].subscribe(func_info['channel'], func_info['func'])

    @staticmethod
    def unregister(func_info):
        application.server['event'].unsubscribe(func_info['channel'], func_info['func'])

event = CheckerEventHandler()
