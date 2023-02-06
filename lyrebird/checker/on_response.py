from lyrebird import application
from .. import checker


class OnResponseHandler:

    def __call__(self, rules=None, rank=0, *args, **kw):
        def func(origin_func):
            func_type = checker.TYPE_ON_RESPONSE
            if not checker.scripts_tmp_storage.get(func_type):
                checker.scripts_tmp_storage[func_type] = []
            checker.scripts_tmp_storage[func_type].append({
                'name': origin_func.__name__,
                'func': origin_func,
                'rules': rules,
                'rank': rank if isinstance(rank, (int, float)) else 0
            })
            return origin_func
        return func

    @staticmethod
    def register(func_info):
        application.on_response.append(func_info)

    @staticmethod
    def unregister(func_info):
        if func_info in application.on_response:
            application.on_response.remove(func_info)

on_response = OnResponseHandler()
