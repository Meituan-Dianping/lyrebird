import json
import codecs
import traceback
import importlib
from pathlib import Path
from lyrebird import log
from lyrebird import application
from lyrebird.mock import context
from lyrebird.event import CustomEventReceiver

logger = log.get_logger()

class NoticeCenter():
    
    def __init__(self):
        self.HISTORY_NOTICE = None
        self.notice_hashmap = {}
        self.notice_list = []
        self.not_remind_list = []
        application.server['event'].subscribe('notice', self.new_notice)
        self.load_history_notice()
        self.load_checkers()

    def load_checkers(self):
        checkers = application.checkers

        SCRIPTS_DIR = Path(application.config.get('checker.workspace'))

        # set checkers status for update
        for checker_name in checkers:
            checkers[checker_name].update = False

        if not SCRIPTS_DIR.exists():
            logger.error('Checker scripts dir not found')
            return checkers

        # load script from ~/.lyrebird/plugin/lyrebird_checker/scripts
        for checker_file in SCRIPTS_DIR.iterdir():
            if not checker_file.name.startswith('_') and not checker_file.name.startswith('.'):
                # Add new checker script
                if checker_file.name not in checkers:
                    checker = Checker(checker_file.name, str(checker_file.absolute()))
                    checkers[checker_file.name] = checker
                checkers[checker_file.name].update = True

        del_name_list = []
        for checker_name in checkers:
            if not checkers[checker_name].update:
                del_name_list.append(checker_name)

        for name in del_name_list:
            del checkers[name]

        logger.debug('------ checkers: ------')
        for checker_name in checkers:
            # update checker status from config
        
            switch_conf = application.config.get('checker.switch', {})
            need_activate = switch_conf.get(checker_name, False)

            checker = checkers[checker_name]
            if need_activate and not checker.activated:
                checker.activate()
            elif not need_activate and checker.activated:
                checker.deactivate()
            logger.debug(checkers[checker_name].json())

    def storage_notice(self, storage_date):
        with codecs.open(self.HISTORY_NOTICE, 'w', 'utf-8') as fp:
            fp.writelines(json.dumps(storage_date))
            fp.flush()

    def notice_hashmap_to_list(self):
        self.notice_list, self.not_remind_list = [], []
        for notice_key, notice in self.notice_hashmap.items():
            notice_info_lastone = notice.get('noticeList')[-1].copy()
            notice_info_lastone.update(
                {
                    'key': notice_key,
                    'count': len(notice.get('noticeList'))
                }
            )
            if notice.get('alert'):
                self.notice_list.append(notice_info_lastone)
            else:
                self.not_remind_list.append(notice_info_lastone)
        self.notice_list.sort(key=lambda x:x['timestamp'], reverse=True)
        self.not_remind_list.sort(key=lambda x:x['timestamp'], reverse=True)

    def update_frontend(self):
        """

        emit data and update frontend
        
        """
        self.notice_hashmap_to_list()
        context.application.socket_io.emit('update')

    def load_history_notice(self):
        """

        load history notice
        
        """
        ROOT = application._cm.root
        DEFAULT_FILENAME = 'notice.json'
        self.HISTORY_NOTICE = ROOT/DEFAULT_FILENAME
        if self.HISTORY_NOTICE.exists() and self.HISTORY_NOTICE.is_file():
            with codecs.open(self.HISTORY_NOTICE, 'r', 'utf-8') as f:
                try:
                    self.notice_hashmap = json.load(f)
                    self.update_frontend()
                except Exception:
                    self.notice_hashmap = {}
                    logger.error('Load history notice fail!')
                    traceback.print_exc()

    def new_notice(self, msg):
        """

        display new notice
        msg: message dict

        
        """
        unique_key = msg.get('message')
        if self.notice_hashmap.get(unique_key):
            self.notice_hashmap[unique_key]['noticeList'].append(msg)
            if self.notice_hashmap[unique_key].get('alert'):
                context.application.socket_io.emit('alert', msg)
        else:
            self.notice_hashmap.update(
                {
                    unique_key: {
                        'alert': True,
                        'noticeList': [msg]
                    }
                }
            )
            context.application.socket_io.emit('alert', msg)

        self.update_frontend()
        self.storage_notice(self.notice_hashmap)

    def change_notice_status(self, unique_key, status):
        """

        change notice alert status, disable notification alert when status is false
        unique_key: str, message unique key
        status: bool, message status
        

        """
        target_notice = self.notice_hashmap.get(unique_key)
        target_notice['alert'] = status
        
        self.update_frontend()
        self.storage_notice(self.notice_hashmap)

    def delete_notice(self, unique_key):
        """

        drop notice group in notice hashmap
        unique_key: str, message unique key
        
        """
        self.notice_hashmap.pop(unique_key)
        self.update_frontend()
        self.storage_notice(self.notice_hashmap)


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
        self._module = script_module = self.loadClass(self.path)
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

    def loadClass(self, py_path):    
        spec = importlib.util.spec_from_file_location('spec', location=py_path)
        target_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(target_module)
        return target_module
