from lyrebird import event
from threading import Thread
import time
import pytest
import lyrebird

from lyrebird import CustomEventReceiver
from lyrebird.mock import context
from lyrebird.mock.context import Application


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
    server = event.EventServer()
    server.start()
    yield server
    server.stop()


def test_event(callback_tester, event_server):

    cb_tester = CallbackTester()

    event_server.subscribe('Test', cb_tester.callback)

    assert event_server.pubsub_channels.get('Test')

    event_server.publish('Test', 'Hello')

    for _ in range(5):
        time.sleep(0.2)
        if len(cb_tester.history) > 0:
            break

    assert len(cb_tester.history) == 1
    assert cb_tester.history[0] == 'Hello'


def test_state(event_server):
    event_server.publish('Test', 'NewActivity', state=True)

    assert event_server.state.get('Test') == 'NewActivity'


def test_state_getter(event_server):
    lyrebird.application.server['event'] = event_server
    test_state = lyrebird.state.get('Test')
    assert test_state == None
    lyrebird.publish('Test', 'TestMessage', state=True)
    test_state = lyrebird.state.get('Test')
    assert test_state == 'TestMessage'


def test_customer_event_alert(event_server):
    custom_event = CustomEventReceiver()
    lyrebird.application.server['event'] = event_server
    custom_event.alert('alert',
                {
                    'message': 'test',
                    'issue': True,
                    'plugin': 'perf.cpu'
                })

    assert custom_event.report_method == 'test_customer_event_alert'
    assert custom_event.report_file[custom_event.report_file.rfind('/') + 1:] == 'test_event.py'


def test_customer_event_alert_not_dict(event_server):
    custom_event = CustomEventReceiver()
    lyrebird.application.server['event'] = event_server
    custom_event.alert('alert', 'a_string')

    assert custom_event.report_method == 'test_customer_event_alert_not_dict'
    assert custom_event.report_file[custom_event.report_file.rfind('/') + 1:] == 'test_event.py'
