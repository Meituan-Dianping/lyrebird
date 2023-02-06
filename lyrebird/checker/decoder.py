from lyrebird import application
from .. import checker


class CustomDecoder:

    def __call__(self, rules=None, rank=0, *args, **kw):
        def func(origin_func):
            func_type = checker.TYPE_DECODER
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
        application.decoder.append(func_info)

    @staticmethod
    def unregister(func_info):
        if func_info in application.decoder:
            application.decoder.remove(func_info)

decoder = CustomDecoder()
