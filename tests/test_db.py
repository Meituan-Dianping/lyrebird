import time
import pytest
from .utils import FakeSocketio, FakeBackgroundTaskServer
from pathlib import Path
from typing import NamedTuple
import lyrebird
from lyrebird import application
from lyrebird.event import EventServer
from lyrebird.config import personal_config_template
from lyrebird.db.database_server import LyrebirdDatabaseServer


MockConfigManager = NamedTuple('MockConfigManager', [('config', dict), ('personal_config', dict), ('ROOT', object), ('root', object)])


@pytest.fixture
def event_server(tmpdir):
    _conf = {
        'ip': '127.0.0.1',
        'mock.port': 9090,
        'event.lyrebird_metrics_report': False
    }
    _personal_conf = personal_config_template
    application._cm = MockConfigManager(config=_conf, personal_config=_personal_conf, ROOT=Path(tmpdir), root=Path(tmpdir))
    lyrebird.mock.context.application.socket_io = FakeSocketio()
    server = EventServer()
    server.start()
    application.server['event'] = server
    yield server
    server.stop()
    application.sync_manager.broadcast_to_queues(None)
    server.terminate()


@pytest.fixture
def task_server():
    lyrebird.application.server['task'] = FakeBackgroundTaskServer()


@pytest.fixture
def db_server():
    server = LyrebirdDatabaseServer()
    server.start()
    application.server['db'] = server
    yield server
    server.stop()


def test_reset(event_server, task_server, db_server):
    publish_time = 3
    channel_name = 'Test'
    message = {
        'message': 'test',
    }

    for _ in range(publish_time):
        event_server.publish(channel_name, message)
    time.sleep(0.2)
    events = db_server.get_event([])
    assert len(events) == publish_time

    db_server.reset()
    events = db_server.get_event([])
    assert len(events) == 0

    for _ in range(publish_time):
        event_server.publish(channel_name, message)
    time.sleep(0.2)
    events = db_server.get_event([])
    assert len(events) == publish_time


def test_get_event_with_multiple_search_str(event_server, task_server, db_server):
    channel_name = 'Test'
    message1 = {
        'message': 'mei',
    }
    message2 = {
        'message': 'tuan',
    }
    message3 = {
        'message': 'meituan',
    }
    message4 = {
        'message': 'meituan dianping',
    }

    event_server.publish(channel_name, message1)
    event_server.publish(channel_name, message2)
    event_server.publish(channel_name, message3)
    event_server.publish(channel_name, message4)
    time.sleep(0.2)
    search_str1 = 'mei'
    search_str2 = 'tuan'
    multiple_search_str = f'{search_str1} + {search_str2}'
    events = db_server.get_event(channel_rules=[], search_str=multiple_search_str)
    assert len(events) == 2
    assert search_str1 in events[0].message
    assert search_str2 in events[0].message
    assert search_str1 in events[1].message
    assert search_str2 in events[1].message
