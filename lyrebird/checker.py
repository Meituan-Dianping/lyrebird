import importlib
from pathlib import Path
from lyrebird import log
from lyrebird import application
from lyrebird.mock import context
from lyrebird.base_server import ThreadServer
from lyrebird.event import CustomEventReceiver
from lyrebird.mock.reporter.report_handler import report


logger = log.get_logger()

class LyrebirdCheckerServer(ThreadServer):
    def __init__(self):
        super().__init__()

        self.SCRIPTS_DIR = Path(application.config.get('checker.workspace'))
        self.checkers = application.checkers
        self.activate_debug_console = False
        self.load_checkers()

        # subscribe all channel for ELK
        # TODO: should not subscribe in init
        application.server['event'].subscribe('any', self.report_to_ELK)

    def load_checkers(self):
        # set checkers status for update
        for checker_name in self.checkers:
            self.checkers[checker_name].update = False

        if not self.SCRIPTS_DIR.exists():
            logger.error('Checker scripts dir not found')
            return

        for checker_file in self.SCRIPTS_DIR.iterdir():
            if not checker_file.name.startswith('_') and not checker_file.name.startswith('.'):
                # Add new checker script
                if checker_file.name not in self.checkers:
                    checker = Checker(checker_file.name, str(checker_file.absolute()))
                    self.checkers[checker_file.name] = checker
                self.checkers[checker_file.name].update = True

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

    def report_to_ELK(self, msg):
        if msg.get('channel') == 'notice':
            msg_sender = msg.get('sender', {})
            report({
                "action": "alert",
                "checker.info": {
                    'module': msg_sender.get('file'),
                    'method': msg_sender.get('function'),
                    'message': msg.get('message')
                }
            })
        if self.activate_debug_console:
            context.application.socket_io.emit('event', msg, namespace='/checker')

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

    @property
    def update(self):
        return self._update

    @update.setter
    def update(self, val):
        self._update = val

    def activate(self):
        self._module = script_module = self.load_class(self.path)
        event_proxy = getattr(script_module, 'event')
        if isinstance(event_proxy, CustomEventReceiver):
            self._event_receiver = event_proxy
            event_proxy.register(context.application.event_bus)
        self.activated = True

    def deactivate(self):
        if self._event_receiver:
            self._event_receiver.unregister(context.application.event_bus)
            self._event_receiver = None
            self._module = None
        self.activated = False

    def json(self):
        return {k: self.__dict__[k] for k in self.__dict__ if not k.startswith('_')}

    def load_class(self, py_path):
        spec = importlib.util.spec_from_file_location('spec', location=py_path)
        target_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(target_module)
        return target_module
