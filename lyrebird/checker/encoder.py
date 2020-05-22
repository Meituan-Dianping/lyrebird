from lyrebird import application
from .. import checker


class CustomEncoder:

    def __call__(self, rules=None, *args, **kw):
        def func(origin_func):
            func_type = checker.TYPE_ENCODER
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
        application.encoder.append(func_info)

    @staticmethod
    def unregister(func_info):
        if func_info in application.encoder:
            application.encoder.remove(func_info)

encoder = CustomEncoder()
