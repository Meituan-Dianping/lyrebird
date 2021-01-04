import imp
import codecs
import shutil
from pathlib import Path
import lyrebird
from lyrebird import log
from lyrebird import application
from lyrebird.mock import context
from lyrebird.base_server import ThreadServer

from .event import event
from .on_request import on_request
from .on_request_upstream import on_request_upstream
from .on_response import on_response
from .on_response_upstream import on_response_upstream
from .encoder import encoder
from .decoder import decoder


logger = log.get_logger()

scripts_tmp_storage = {}

TYPE_EVENT = 'event'
TYPE_ON_REQUEST = 'on_request'
TYPE_ON_REQUEST_UPSTREAM = 'on_request_upstream'
TYPE_ON_RESPONSE = 'on_response'
TYPE_ON_RESPONSE_UPSTREAM = 'on_response_upstream'
TYPE_ENCODER = 'encoder'
TYPE_DECODER = 'decoder'

FUNC_MAP_HANDLERS = {
    TYPE_EVENT: event,
    TYPE_ON_REQUEST: on_request,
    TYPE_ON_REQUEST_UPSTREAM: on_request_upstream,
    TYPE_ON_RESPONSE: on_response,
    TYPE_ON_RESPONSE_UPSTREAM: on_response_upstream,
    TYPE_ENCODER: encoder,
    TYPE_DECODER: decoder
}


class LyrebirdCheckerServer(ThreadServer):
    def __init__(self):
        super().__init__()

        ROOT = Path(lyrebird.APPLICATION_CONF_DIR)
        self.SCRIPTS_DIR_TEMPLATE = ROOT/'checkers'
        self.EXAMPLE_DIR = Path(__file__).parent.parent/'examples'/'checkers'

        self.checkers = application.checkers
        self.load_checkers()

    def load_checkers(self):
        for checker_name in self.checkers:
            self.checkers[checker_name].update = False

        scripts_list = self.get_checker_list()
        if not scripts_list:
            return

        for checker_file in scripts_list:
            self.init_checker(checker_file.name, str(checker_file.absolute()))

        self.delete_unupdated_checker()

        logger.debug('------ checkers: ------')
        for name, checker in self.checkers.items():
            switch_conf = application.config.get('checker.switch', {})
            need_activate = switch_conf.get(name, False)
            self.activate_checker(checker, need_activate)

    def get_checker_list(self):
        workspace_str = application.config.get('checker.workspace')

        if workspace_str:
            workspace = Path(workspace_str)
            if not workspace.expanduser().exists():
                logger.error(f'Checker scripts dir {workspace_str} not found!')
                return
            workspace_iterdir = self.get_iterdir_python(workspace)
            if not workspace_iterdir:
                logger.warning(f'No checker script found in dir {workspace_str}')
                return

        else:
            workspace = Path(self.SCRIPTS_DIR_TEMPLATE)
            workspace.mkdir(parents=True, exist_ok=True)
            workspace_iterdir = self.get_iterdir_python(workspace)
            if not workspace_iterdir:
                self.copy_example_scripts()

        return workspace_iterdir

    @staticmethod
    def get_iterdir_python(path):
        path = Path(path)
        end_str = '.py'
        scripts_list = [i for i in path.iterdir() if i.suffix == end_str]
        return scripts_list

    def copy_example_scripts(self):
        for example in self.EXAMPLE_DIR.iterdir():
            if not example.name.endswith('.py'):
                continue
            dst = self.SCRIPTS_DIR_TEMPLATE / example.name
            shutil.copy(example, dst)

    def init_checker(self, name, path):
        checker = Checker(name, path)
        self.checkers[name] = checker

    def delete_unupdated_checker(self):
        del_name_list = []
        for name, checker in self.checkers.items():
            if not checker.update:
                del_name_list.append(name)

        for name in del_name_list:
            del self.checkers[name]

    def activate_checker(self, checker, need_activate):
        if need_activate and not checker.activated:
            checker.activate()
        elif not need_activate and checker.activated:
            checker.deactivate()
        logger.debug(checker.json())

    def load_scripts(self, scripts):
        scripts_list = [Path(s).expanduser() for s in scripts]
        for checker_file in scripts_list:
            self.init_checker(checker_file.name, str(checker_file.absolute()))
            self.activate_checker(self.checkers[checker_file.name], True)
            self.checkers[checker_file.name].debug = True

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
        self.debug = False
        self._module = None
        self._update = False
        self._funcs_map = {}

        try:
            self._load_checker()
        except Exception as e:
            logger.error(f'Load checker {self.name} error:\n{e}\nfile path: {self.path}')

    @property
    def update(self):
        return self._update

    @update.setter
    def update(self, val):
        self._update = val

    def _load_checker(self):
        try:
            self._module = imp.load_source(self.name, self.path)
        except Exception as e:
            self.update = False
            raise CheckerIllegal(e)

        self.update = True
        self._checker_detection()
        global scripts_tmp_storage
        for func_type, func_list in scripts_tmp_storage.items():
            self._funcs_map[func_type] = [f for f in func_list]
        scripts_tmp_storage = {}

    def _checker_detection(self):
        if hasattr(self._module, TYPE_ENCODER) and not hasattr(self._module, TYPE_DECODER):
            logger.warning(f'Load checker {self.name} error: Encoder contains, but decoder not found!')

        if hasattr(self._module, TYPE_DECODER) and not hasattr(self._module, TYPE_ENCODER):
            logger.warning(f'Load checker {self.name} error: Decoder contains, but encoder not found!')

    def activate(self):
        for func_type, func_list in self._funcs_map.items():
            handler = FUNC_MAP_HANDLERS.get(func_type)
            if not handler:
                logger.error('Unhandler this func: ' + func_type)
                continue

            for func_info in func_list:
                handler.register(func_info)

        self.activated = True

    def deactivate(self):
        for func_type, func_list in self._funcs_map.items():
            handler = FUNC_MAP_HANDLERS.get(func_type)
            if not handler:
                logger.error('Unhandler this func: ' + func_type)
                continue

            for func_info in func_list:
                handler.unregister(func_info)

        self.activated = False

    def read(self):
        content = ''
        with codecs.open(self.path, 'r', 'utf-8') as f:
            content = f.read()
        return content

    def write(self, data):
        origin_activate_status = self.activated
        if origin_activate_status:
            self.deactivate()

        with codecs.open(self.path, 'w', 'utf-8') as f:
            f.write(data)
        self._load_checker()

        if origin_activate_status:
            self.activate()

    def json(self):
        return {k: self.__dict__[k] for k in self.__dict__ if not k.startswith('_')}

class CheckerIllegal(Exception):
    pass
