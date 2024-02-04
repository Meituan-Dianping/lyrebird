from lyrebird import application
from .. import checker
import functools


class OnRequestHandler:

    def __call__(self, rules=None, rank=0, modifiy_request_body=True, *args, **kw):
        def func(origin_func):
            func_type = checker.TYPE_ON_REQUEST
            if not checker.scripts_tmp_storage.get(func_type):
                checker.scripts_tmp_storage[func_type] = []
            origin_func = self.modifiy_request_body_decorator(origin_func, modifiy_request_body)
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
        application.on_request.append(func_info)

    @staticmethod
    def unregister(func_info):
        if func_info in application.on_request:
            application.on_request.remove(func_info)

    @staticmethod
    def modifiy_request_body_decorator(func, modifiy_request_body):
        # When the request modifier modifies only headers or urls, 
        # ensure that the Origin request body switch is still in effect after the request modifier is triggered
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if isinstance(args, (list, tuple)) and len(args) > 0 and isinstance(args[0], dict):
                if 'keep_origin_request_body' in args[0]:
                    # When multiple request modifiers are triggered, the original request data is not used as long as one modifies the requestBody
                    args[0]['keep_origin_request_body'] = args[0]['keep_origin_request_body'] and not modifiy_request_body
                else:
                    args[0]['keep_origin_request_body'] = not modifiy_request_body
            return result
        return wrapper

on_request = OnRequestHandler()
