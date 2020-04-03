import json
import codecs
import traceback
import lyrebird
from pathlib import Path
from lyrebird import log
from lyrebird import application
from lyrebird.mock import context

logger = log.get_logger()

class NoticeCenter():

    def __init__(self):
        self.HISTORY_NOTICE = None
        self.notice_hashmap = {}
        self.notice_list = []
        self.not_remind_list = []
        application.server['event'].subscribe('notice', self.new_notice)
        self.load_history_notice()

    def storage_notice(self, storage_date):
        with codecs.open(self.HISTORY_NOTICE, 'w', 'utf-8') as fp:
            fp.writelines(json.dumps(storage_date, ensure_ascii=False, indent=4))
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
        ROOT = Path(lyrebird.APPLICATION_CONF_DIR)
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
        unique_key = msg.get('title')
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
