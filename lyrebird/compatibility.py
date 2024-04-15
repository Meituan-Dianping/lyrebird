from lyrebird import application, log
import importlib.util
import platform
import sys
import inspect
from multiprocessing.managers import Namespace

logger = log.get_logger()


application_white_map = {
    'config',
    '_cm'
}


context_white_map = {
    'application.data_manager.activated_data',
    'application.data_manager.activated_group'
}


decorator_compat_code = '''
def jit(*args, **kwargs):
    def decorator(func):
        print(f"{func.__name__} run in a cover function")
        return func
    return decorator
'''

PYTHON_MIN_VERSION = (3, 8, 0)
PYTHON_MAX_VERSION = (3, 11, float('inf'))

def import_compat_util(module_name:str, module_content:list):
    module_spec = importlib.util.spec_from_loader(module_name, loader=None, origin='string', is_package=False)
    module_obj = importlib.util.module_from_spec(module_spec)
    for code in module_content:
        exec(code, module_obj.__dict__)
    sys.modules[module_name] = module_obj


def compat_check():
    return compat_python_version()


def compat_numba():
    try:
        import numba
    except Exception as e:
        logger.error(f'numba import failed. Please check that the library is installed correctly in your python environment')
        import_compat_util('numba', [decorator_compat_code])
        return False
    return True


def compat_redis():
    try:
        import redis
    except Exception as e:
        logger.error(f'redis import failed. Please check that the library is installed correctly in your python environment')
        return False
    return True


def compat_python_version():
    version = platform.python_version_tuple()
    major = int(version[0])
    minor = int(version[1])
    minor_minor = int(version[2])
    if major < PYTHON_MIN_VERSION[0] or \
    (major == PYTHON_MIN_VERSION[0] and minor < PYTHON_MIN_VERSION[1]) or \
    (major == PYTHON_MIN_VERSION[0] and minor == PYTHON_MIN_VERSION[1] and minor_minor == PYTHON_MIN_VERSION[2]):
        msg = (
            'The python version is too early. Please use Python version '
            f'{PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]}.{PYTHON_MIN_VERSION[2]} or later.'
        )
        logger.error(msg)
        return False
    if major > PYTHON_MIN_VERSION[0] or \
    (major == PYTHON_MIN_VERSION[0] and minor > PYTHON_MIN_VERSION[1]) or \
    (major == PYTHON_MIN_VERSION[0] and minor == PYTHON_MIN_VERSION[1] and minor_minor > PYTHON_MIN_VERSION[2]):
        msg = (
            'python version is too high, Lyrebird is not supported,'
            'the current Lyrebird support version is '
            f'{PYTHON_MIN_VERSION[0]}.{PYTHON_MIN_VERSION[1]}.{"x" if isinstance(PYTHON_MIN_VERSION[2], float) else PYTHON_MIN_VERSION[2]}.'
        )
        logger.warning(msg)
    return True


def prepare_application_for_monkey_patch() -> Namespace:
    from lyrebird import application, context
    namespace = application.sync_manager.get_namespace()
    namespace.application = CheckerApplicationInfo(application, application_white_map)
    namespace.context = CheckerApplicationInfo(context, context_white_map)
    namespace.queue = application.server['event'].event_queue
    return namespace


def monkey_patch_application(async_obj, async_funcs=None):
    import lyrebird
    from lyrebird.event import EventServer
    from lyrebird import event

    msg_queue = async_obj['msg_queue']
    process_namespace = async_obj['process_namespace']
    
    lyrebird.application = process_namespace.application
    lyrebird.application.config = process_namespace.application._cm.config
    lyrebird.context = process_namespace.context

    if async_funcs:
        checker_event_server = EventServer(True)
        checker_event_server.event_queue = msg_queue
        lyrebird.application['server'] = CheckerApplicationInfo()
        lyrebird.application.server['event'] = checker_event_server
        checker_event_server.__class__.publish = async_funcs['publish']
        event.__class__.publish = async_funcs['publish']
        event.__class__.issue = async_funcs['issue']


def monkey_patch_publish(channel, message, publish_queue, *args, **kwargs):
    from lyrebird.event import EventServer
    from lyrebird.checker.event import CheckerEventHandler
    if channel == 'notice':
        CheckerEventHandler.check_notice(message)
    
    event_id, channel, message = EventServer.get_publish_message(channel, message)
    publish_queue.put((event_id, channel, message, args, kwargs))


def monkey_patch_issue(title, message, publish_queue, *args, **kwargs):
    from lyrebird.event import EventServer
    from lyrebird.checker.event import CheckerEventHandler
    notice = {
        "title": title,
        "message": message
    }
    CheckerEventHandler.check_notice(notice)

    event_id, channel, message = EventServer.get_publish_message('notice', notice)
    publish_queue.put((event_id, channel, message, args, kwargs))


class CheckerApplicationInfo(dict):

    def __init__(self, data=None, white_map={}):
        super().__init__()
        for path in white_map:
            value = self._get_value_from_path(data, path)
            if value is not None:
                self._set_value_to_path(path, value)

    def _get_value_from_path(self, data, path):
        keys = path.split('.')
        value = data
        for key in keys:
            value = getattr(value, key)
            if value is None:
                return None
        return value

    def _set_value_to_path(self, path, value):
        keys = path.split('.')
        current_dict = self
        for key in keys[:-1]:
            if key not in current_dict:
                current_dict[key] = CheckerApplicationInfo()
            current_dict = current_dict[key]
        current_dict[keys[-1]] = value

    
    def __getattr__(self, item):
        value = self
        for key in item.split('.'):
            value = value.get(key)
            if value is None:
                break
        return value

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, item):
        del self[item]
