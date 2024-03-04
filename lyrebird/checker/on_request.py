from lyrebird import application
from .. import checker


class OnRequestHandler:

    def __call__(self, rules=None, rank=0, modify_request_body=True, *args, **kw):
        def func(origin_func):
            func_type = checker.TYPE_ON_REQUEST
            if not checker.scripts_tmp_storage.get(func_type):
                checker.scripts_tmp_storage[func_type] = []
            checker.scripts_tmp_storage[func_type].append({
                'name': origin_func.__name__,
                'func': origin_func,
                'rules': rules,
                'rank': rank if isinstance(rank, (int, float)) else 0,
                'modify_request_body': modify_request_body
            })
            return origin_func
        return func

    @staticmethod
    def register(func_info):
        func_info['func'] = checker.DecoratorUtils.modify_request_body_decorator(func_info['func'], func_info['modify_request_body'])
        application.on_request.append(func_info)

    @staticmethod
    def unregister(func_info):
        if func_info in application.on_request:
            application.on_request.remove(func_info)


on_request = OnRequestHandler()
