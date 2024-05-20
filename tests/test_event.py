import time
import pytest
import lyrebird
from .utils import FakeSocketio, FakeBackgroundTaskServer
from typing import NamedTuple
from lyrebird import application
from lyrebird.event import EventServer
from lyrebird import CustomEventReceiver


MockConfigManager = NamedTuple('MockConfigManager', [('config', dict)])


class CallbackTester:

    def __init__(self):
        self.history = []

    def callback(self, msg):
        self.history.append(msg)


@pytest.fixture
def callback_tester():
    return CallbackTester()


@pytest.fixture
def event_server():
    _conf = {
        'ip': '127.0.0.1',
        'mock.port': 9090,
        'event.lyrebird_metrics_report': False
    }
    application._cm = MockConfigManager(config=_conf)
    lyrebird.mock.context.application.socket_io = FakeSocketio()
    server = EventServer()
    server.start()
    lyrebird.application.server['event'] = server
    yield server
    server.stop()
    application.sync_manager.broadcast_to_queues(None)
    server.terminate()


@pytest.fixture
def task_server():
    server = FakeBackgroundTaskServer()
    lyrebird.application.server['task'] = server
    yield server


def test_event(callback_tester, event_server, task_server):

    cb_tester = CallbackTester()

    event_server.subscribe({'channel':'Test', 'func':cb_tester.callback})

    assert event_server.pubsub_channels.get('Test')

    for _ in range(1000):
        event_server.publish('Test', 'Hello')

    for _ in range(5):
        time.sleep(0.2)
        if len(cb_tester.history) > 0:
            break

    assert len(cb_tester.history) == 1000
    assert cb_tester.history[0] == 'Hello'


def test_event_default_information(callback_tester, event_server, task_server):

    cb_tester = CallbackTester()

    event_server.subscribe({'channel':'Test', 'func':cb_tester.callback})

    assert event_server.pubsub_channels.get('Test')

    test = {
        'message': 'test',
    }

    event_server.publish('Test', test)
    time.sleep(0.2)
    resent_history = cb_tester.history[0]
    assert resent_history.get('message') == 'test'
    assert resent_history.get('channel') == 'Test'


def test_event_default_information_with_sender(callback_tester, event_server, task_server):

    cb_tester = CallbackTester()

    event_server.subscribe({'channel':'Test', 'func':cb_tester.callback})

    assert event_server.pubsub_channels.get('Test')

    test = {}

    event_server.publish('Test', test)
    time.sleep(0.2)
    resent_history = cb_tester.history[-1]
    assert resent_history.get('message') == None
    assert resent_history.get('channel') == 'Test'


def test_state(event_server, task_server):
    event_server.publish('Test', 'NewActivity', state=True)

    assert event_server.state.get('Test') == 'NewActivity'


def test_state_getter(event_server, task_server):
    test_state = lyrebird.state.get('Test')
    assert test_state == None
    lyrebird.publish('Test', 'TestMessage', state=True)
    test_state = lyrebird.state.get('Test')
    assert test_state == 'TestMessage'


def test_customer_event_issue(event_server):
    custom_event = CustomEventReceiver()
    issue_message = 'test'
    custom_event.issue('issue_string', issue_message)

    def msg_receiver(msg):
        assert msg.get('sender') == 'test_event.py'
        assert msg.get('message') == 'issue_string'

    lyrebird.subscribe('notice', msg_receiver)
