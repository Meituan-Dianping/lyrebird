import imp
import shutil
import importlib
from pathlib import Path
from lyrebird import log
from lyrebird import application
from lyrebird.mock import context
from lyrebird.base_server import ThreadServer
from lyrebird.event import CustomEventReceiver


logger = log.get_logger()


class LyrebirdCheckerServer(ThreadServer):
    def __init__(self):
        super().__init__()

        ROOT = application._cm.root
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
                for event in class_module.event.listeners:
                    application.server['event'].subscribe(event['channel'], event['func'])
            except ValueError:
                logger.error(f'{path} failed to load. Only python file is allowed.')

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
