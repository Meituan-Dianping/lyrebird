from lyrebird import application
from .. import checker


class OnRequestHandler:

    def __call__(self, rules=None, *args, **kw):
        def func(origin_func):
            func_type = checker.TYPE_ON_REQUEST
            if not checker.scripts_tmp_storage.get(func_type):
                checker.scripts_tmp_storage[func_type] = []
            checker.scripts_tmp_storage[func_type].append({
                'name': origin_func.__name__,
                'func': origin_func,
                'rules': rules
            })
            return origin_func
        return func

    @staticmethod
    def register(func_info):
        application.on_request.append(func_info)

    @staticmethod
    def unregister(func_info):
        if func_info in application.on_request:
            application.on_request.remove(func_info)

on_request = OnRequestHandler()
