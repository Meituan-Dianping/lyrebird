from typing import NamedTuple
from lyrebird.mock import context
from lyrebird.notice_center import NoticeCenter
from lyrebird import reporter
from lyrebird import application
from lyrebird.event import EventServer
from lyrebird.task import BackgroundTaskServer

import pytest

MockConfigManager = NamedTuple('MockConfigManager', [('config', dict)])

NOTICE = {
    "title": "1st title",
    "message": "1st message",
    "timestamp": 1,
    "sender": {
        "file": "test.py",
        "function": "func"
    },
    "channel": "notice"
}


@pytest.fixture
def notice_center(tmpdir):
    def emit(*args, **kwargs):pass
    context.application.socket_io = type('MockedSocketIO', (), {'emit': emit})()
    notice_center = NoticeCenter()
    notice_center.HISTORY_NOTICE = str(tmpdir) + '/notice.json'
    return notice_center


@pytest.fixture
def event_server():
    _conf = {
        'ip': '127.0.0.1',
        'mock.port': 9090
    }
    application.sync_manager = application.SyncManager()
    application._cm = MockConfigManager(config=_conf)
    server = EventServer()
    server.start()
    application.server['event'] = server
    yield server
    server.stop()
    application.sync_manager.broadcast_to_queues(None)
    server.terminate()


@pytest.fixture
def task_server():
    application.reporter = reporter.Reporter()
    server = BackgroundTaskServer()
    server.start()
    application.server['task'] = server
    yield server
    server.stop()


def test_new_notice(event_server, task_server, notice_center):
    notice_center.notice_hashmap = {}
    notice_center.new_notice(NOTICE)
    test_str = NOTICE.get('title')
    assert bool(notice_center.notice_hashmap.get(test_str)) == True


def test_new_notices(event_server, task_server, notice_center):
    notice_center.notice_hashmap = {}
    times = 10
    for _ in range(times):
        notice_center.new_notice(NOTICE)
    test_str = NOTICE.get('title')
    len_notice_hashmap = len(notice_center.notice_hashmap)
    assert len_notice_hashmap == 1

    len_notice_list = len(notice_center.notice_hashmap[test_str].get('noticeList'))
    assert len_notice_list == times


def test_change_notice_status(event_server, task_server, notice_center):
    notice_center.notice_hashmap = {}
    notice_center.new_notice(NOTICE)
    test_str = '1st title'
    test_status = True
    notice_center.change_notice_status(test_str, test_status)
    assert notice_center.notice_hashmap[test_str].get('alert') == test_status


def test_delete_notice(event_server, task_server, notice_center):
    notice_center.notice_hashmap = {}
    notice_center.new_notice(NOTICE)
    test_str = '1st title'
    notice_center.delete_notice(test_str)
    assert notice_center.notice_hashmap.get(test_str) == None
