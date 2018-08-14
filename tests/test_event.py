from lyrebird import event
from threading import Thread
import time
import pytest

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
    import lyrebird
    lyrebird.application.server['event'] = event_server
    test_state = lyrebird.state.get('Test')
    assert test_state == None
    event_server.publish('Test', 'TestMessage', state=True)
    test_state = lyrebird.state.get('Test')
    assert test_state == 'TestMessage'
