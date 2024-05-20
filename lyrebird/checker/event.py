import inspect
from lyrebird import application
from .. import checker


class CheckerEventHandler:

    def __call__(self, channel, process=True, *args, **kw):
        def func(origin_func):
            if not checker.scripts_tmp_storage.get(checker.TYPE_EVENT):
                checker.scripts_tmp_storage[checker.TYPE_EVENT] = []
            checker.scripts_tmp_storage[checker.TYPE_EVENT].append({
                'name': origin_func.__name__,
                'origin': origin_func.__code__.co_filename,
                'func': origin_func,
                'channel': channel,
                'process': process
            })
            return origin_func
        return func

    def issue(self, title, message):
        from lyrebird import application
        notice = {
            "title": title,
            "message": message
        }
        self.__class__.check_notice(notice)
        application.server['event'].publish('notice', notice)

    def publish(self, channel, message, *args, **kwargs):
        from lyrebird import application
        if channel == 'notice':
            self.__class__.check_notice(message)
        application.server['event'].publish(channel, message, *args, **kwargs)
    
    @staticmethod
    def check_notice(notice):
        from lyrebird import application
        stack = inspect.stack()
        script_path = stack[2].filename
        script_name = script_path[script_path.rfind('/') + 1:]
        if script_name in application.config.get('event.notice.autoissue.checker', []):
            notice['title'] = f"【Extension】{notice.get('title')}"
            notice['alert'] = False

    @staticmethod
    def register(func_info):
        application.server['event'].subscribe(func_info)

    @staticmethod
    def unregister(func_info):
        application.server['event'].unsubscribe(func_info)

event = CheckerEventHandler()
