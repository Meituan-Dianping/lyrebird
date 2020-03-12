import imp
import shutil
import importlib
from pathlib import Path
import lyrebird
from lyrebird import log
from lyrebird import application
from lyrebird.mock import context
from lyrebird.base_server import ThreadServer
from lyrebird.event import CustomEventReceiver


logger = log.get_logger()


registered_func_array = []


class CheckerEventHandler:

    def __call__(self, channel, *args, **kw):
        def func(origin_func):
            registered_func_array.append([channel, origin_func])
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


event = CheckerEventHandler()

encoders = []
encoder_func_array = []


class EncoderHandler:

    def __call__(self, *args, **kw):
        def func(origin_func):
            encoder_func_array.append(origin_func)
            return origin_func
        return func


encoder = EncoderHandler()


on_request_func_array = []
on_response_func_array = []
on_request_upstream_func_array = []
on_response_upstream_func_array = []


class OnRequestHandler:

    def __call__(self, rules=None, *args, **kw):
        def func(origin_func):
            on_request_func_array.append({
                'name': origin_func.__name__,
                'func': origin_func,
                'rules': rules
            })
            return origin_func
        return func


class OnResponseHandler:

    def __call__(self, rules=None, *args, **kw):
        def func(origin_func):
            on_response_func_array.append({
                'name': origin_func.__name__,
                'func': origin_func,
                'rules': rules
            })
            return origin_func
        return func


class OnRequestUpstreamHandler:

    def __call__(self, rules=None, *args, **kw):
        def func(origin_func):
            on_request_upstream_func_array.append({
                'name': origin_func.__name__,
                'func': origin_func,
                'rules': rules
            })
            return origin_func
        return func


class OnResponseUpstreamHandler:

    def __call__(self, rules=None, *args, **kw):
        def func(origin_func):
            on_response_upstream_func_array.append({
                'name': origin_func.__name__,
                'func': origin_func,
                'rules': rules
            })
            return origin_func
        return func


on_request = OnRequestHandler()
on_response = OnResponseHandler()
on_request_upstream = OnRequestUpstreamHandler()
on_response_upstream = OnResponseUpstreamHandler()


class LyrebirdCheckerServer(ThreadServer):
    def __init__(self):
        super().__init__()

        ROOT = Path(lyrebird.APPLICATION_CONF_DIR)
        self.SCRIPTS_DIR_TEMPLATE = ROOT/'checkers'
        self.EXAMPLE_DIR = Path(__file__).parent/'examples'/'checkers'

        self.scripts_dir = None
        self.checkers = application.checkers
        self.load_checkers()

        # subscribe all channel for ELK
        # TODO: should not subscribe in init
        application.server['event'].subscribe('any', self.send_report)

    def load_checkers(self):
        # set checkers status for update
        for checker_name in self.checkers:
            self.checkers[checker_name].update = False

        # get checker workspace
        if application.config.get('checker.workspace'):
            self.scripts_dir = Path(application.config.get('checker.workspace'))
            if not self.scripts_dir.exists():
                logger.error('Checker scripts dir not found')
                return
        else:
            self.scripts_dir = self.SCRIPTS_DIR_TEMPLATE
            self.scripts_dir.mkdir(parents=True, exist_ok=True)

        # get checker files
        scripts_list = [script for script in self.scripts_dir.iterdir() if script.name.endswith('.py')]

        # load examples if scripts_dir has no python script
        if not scripts_list:
            for example in self.EXAMPLE_DIR.iterdir():
                if example.name.endswith('.py'):
                    dst = self.SCRIPTS_DIR_TEMPLATE / example.name
                    shutil.copy(example, dst)

        for checker_file in self.scripts_dir.iterdir():
            # Add new checker script
            if checker_file.name.endswith('.py'):
                self.init_checker(checker_file.name, str(checker_file.absolute()))

        del_name_list = []
        for checker_name in self.checkers:
            if not self.checkers[checker_name].update:
                del_name_list.append(checker_name)

        for name in del_name_list:
            del self.checkers[name]

        logger.debug('------ checkers: ------')
        for checker_name in self.checkers:
            # update checker status from config
            switch_conf = application.config.get('checker.switch', {})
            need_activate = switch_conf.get(checker_name, False)

            checker = self.checkers[checker_name]
            if need_activate and not checker.activated:
                checker.activate()
            elif not need_activate and checker.activated:
                checker.deactivate()
            logger.debug(self.checkers[checker_name].json())

    def init_checker(self, name, path):
        if name not in self.checkers:
            checker = Checker(name, path)
            self.checkers[name] = checker
        self.checkers[name].update = True

    def send_report(self, msg):
        if isinstance(msg, dict) and msg.get('channel') == 'notice':
            msg_sender = msg.get('sender', {})
            application.reporter.report({
                "action": "alert",
                "checker.info": {
                    'module': msg_sender.get('file'),
                    'method': msg_sender.get('function'),
                    'message': msg.get('title')
                }
            })

    def load_scripts(self, scripts):
        for path in scripts:
            try:
                class_module = imp.load_source('checker', path)
                self._load_event_handler(class_module)
                # TODO Decoder
                self._load_encoder_handler(class_module)
                self._load_on_request_handler(class_module)
                self._load_on_response_handler(class_module)
                self._load_on_request_upstream_handler(class_module)
                self._load_on_response_upstream_handler(class_module)
            except ValueError:
                logger.error(f'{path} failed to load. Only python file is allowed.')

    def _load_event_handler(self, checker_class_module):
        if not hasattr(checker_class_module, 'event'):
            return
        if isinstance(checker_class_module.event, CustomEventReceiver):
            for event in checker_class_module.event.listeners:
                application.server['event'].subscribe(event['channel'], event['func'])
        elif isinstance(checker_class_module.event, CheckerEventHandler):
            global registered_func_array
            for registered_func in registered_func_array:
                application.server['event'].subscribe(registered_func[0], registered_func[1])
            registered_func_array = []

    def _load_encoder_handler(self, checker_class_module):
        if not hasattr(checker_class_module, 'encoder'):
            return
        global encoder_func_array
        global encoders
        for encoder_func in encoder_func_array:
            encoders.append(encoder_func)
        encoder_func_array = []

    def _load_on_request_handler(self, script_module):
        if not hasattr(script_module, 'on_request'):
            return
        global on_request_func_array
        for func in on_request_func_array:
            application.on_request.append(func)
        on_request_func_array = []

    def _load_on_response_handler(self, script_module):
        if not hasattr(script_module, 'on_response'):
            return
        global on_response_func_array
        for func in on_response_func_array:
            application.on_response.append(func)
        on_response_func_array = []

    def _load_on_request_upstream_handler(self, script_module):
        if not hasattr(script_module, 'on_request_upstream'):
            return
        global on_request_upstream_func_array
        for func in on_request_upstream_func_array:
            application.on_request_upstream.append(func)
        on_request_upstream_func_array = []

    def _load_on_response_upstream_handler(self, script_module):
        if not hasattr(script_module, 'on_response_upstream'):
            return
        global on_response_upstream_func_array
        for func in on_response_upstream_func_array:
            application.on_response_upstream.append(func)
        on_response_upstream_func_array = []

    def run(self):
        super().run()

    def stop(self):
        super().stop()


class Checker:
    def __init__(self, name, path):
        self.name = name
        self.activated = False
        self.path = path
        self.select = False
        self._module = None
        self._event_receiver = None
        self._update = False
        self._encoder_func_list = []
        self._on_request_func_list = []
        self._on_response_func_list = []
        self._on_request_upstream_func_list = []
        self._on_response_upstream_func_list = []

    @property
    def update(self):
        return self._update

    @update.setter
    def update(self, val):
        self._update = val

    def activate(self):
        self._module = self.load_class(self.path)
        self._register_event_callback_func()
        self._register_encoder_callback_func()
        self._register_on_request_callback_func()
        self._register_on_response_callback_func()
        self._register_on_request_upstream_callback_func()
        self._register_on_response_upstream_callback_func()
        self.activated = True

    def deactivate(self):
        self._unregister_event_callback_func()
        self._unregister_encoder_callback_func()
        self._unregister_on_request_callback_func()
        self._unregister_on_response_callback_func()
        self._unregister_on_request_upstream_callback_func()
        self._unregister_on_response_upstream_callback_func()
        self.activated = False

    def _register_event_callback_func(self):
        script_module = self._module
        if not hasattr(script_module, 'event'):
            return

        global registered_func_array
        event_proxy = getattr(script_module, 'event')
        if isinstance(event_proxy, CustomEventReceiver):
            self._event_receiver = event_proxy
            event_proxy.register(context.application.event_bus)
        elif isinstance(event_proxy, CheckerEventHandler):
            self._event_receiver = CustomEventReceiver()
            for registered_func in registered_func_array:
                self._event_receiver.listeners.append(dict(channel=registered_func[0], func=registered_func[1]))
            self._event_receiver.register(context.application.event_bus)
            registered_func_array = []

    def _unregister_event_callback_func(self):
        if not self._event_receiver:
            return
        self._event_receiver.unregister(context.application.event_bus)
        self._event_receiver = None
        self._module = None

    def _register_encoder_callback_func(self):
        if not hasattr(self._module, 'encoder'):
            return
        global encoder_func_array
        global encoders
        for encoder_func in encoder_func_array:
            encoders.append(encoder_func)
            self._encoder_func_list.append(encoder_func)
        encoder_func_array = []

    def _unregister_encoder_callback_func(self):
        global encoders
        for encoder_func in self._encoder_func_list:
            if encoder_func not in encoders:
                continue
            encoders.remove(encoder_func)

    def _register_on_request_callback_func(self):
        if not hasattr(self._module, 'on_request'):
            return
        global on_request_func_array
        for func in on_request_func_array:
            self._on_request_func_list.append(func['func'])
            application.on_request.append(func)
        on_request_func_array = []

    def _unregister_on_request_callback_func(self):
        for func_obj in application.on_request[::-1]:
            if func_obj['func'] not in self._on_request_func_list:
                continue
            application.on_request.remove(func_obj)

    def _register_on_response_callback_func(self):
        if not hasattr(self._module, 'on_response'):
            return
        global on_response_func_array
        for func in on_response_func_array:
            self._on_response_func_list.append(func['func'])
            application.on_response.append(func)
        on_response_func_array = []

    def _unregister_on_response_callback_func(self):
        for func_obj in application.on_response[::-1]:
            if func_obj['func'] not in self._on_response_func_list:
                continue
            application.on_response.remove(func_obj)

    def _register_on_request_upstream_callback_func(self):
        if not hasattr(self._module, 'on_request_upstream'):
            return
        global on_request_upstream_func_array
        for func in on_request_upstream_func_array:
            self._on_request_upstream_func_list.append(func['func'])
            application.on_request_upstream.append(func)
        on_request_upstream_func_array = []

    def _unregister_on_request_upstream_callback_func(self):
        for func_obj in application.on_request_upstream[::-1]:
            if func_obj['func'] not in self._on_request_upstream_func_list:
                continue
            application.on_request_upstream.remove(func_obj)

    def _register_on_response_upstream_callback_func(self):
        if not hasattr(self._module, 'on_response_upstream'):
            return
        global on_response_upstream_func_array
        for func in on_response_upstream_func_array:
            self._on_response_upstream_func_list.append(func['func'])
            application.on_response_upstream.append(func)
        on_response_upstream_func_array = []

    def _unregister_on_response_upstream_callback_func(self):
        for func_obj in application.on_response_upstream[::-1]:
            if func_obj['func'] not in self._on_response_upstream_func_list:
                continue
            application.on_response_upstream.remove(func_obj)

    def json(self):
        return {k: self.__dict__[k] for k in self.__dict__ if not k.startswith('_')}

    def load_class(self, py_path):
        spec = importlib.util.spec_from_file_location('spec', location=py_path)
        target_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(target_module)
        return target_module
