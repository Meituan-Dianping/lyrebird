import pytest
from lyrebird import event
from lyrebird import application
from lyrebird.checker import LyrebirdCheckerServer

CHECKER_A_FILENAME = "checker_a.py"
CHECKER_B_FILENAME = "checker_b.py"
CHECKER_A_SWITCH = True
CHECKER_B_SWITCH = False

@pytest.fixture
def checker_init(tmp_path):
    # default config
    config = {
        "checker.workspace": tmp_path,
        "checker.switch": {
            CHECKER_A_FILENAME: CHECKER_A_SWITCH,
            CHECKER_B_FILENAME: CHECKER_B_SWITCH
        }
    }

    # init file dir
    content = u"from lyrebird import CustomEventReceiver\nevent = CustomEventReceiver()\n@event('flow')\ndef test_func():\n\tpass"
    checker_a_file = tmp_path / CHECKER_A_FILENAME
    checker_a_file.write_text(content)
    checker_b_file = tmp_path / CHECKER_B_FILENAME
    checker_b_file.write_text(content)

    # mock config
    application._cm = type('MockedContentManager', (), {'config': config})()

    return application.checkers

@pytest.fixture
def checker_server(checker_init, tmp_path):
    server = LyrebirdCheckerServer()
    server.start()
    server.SCRIPTS_DIR = tmp_path
    application.server['checker'] = server
    yield server
    server.stop()


@pytest.fixture
def event_server():
    server = event.EventServer()
    application.server['event'] = server
    yield server


def test_load_checkers(event_server, checker_server):
    assert CHECKER_A_FILENAME in application.checkers
    assert len(application.checkers) == 2

    checker_a_info = application.checkers[CHECKER_A_FILENAME].json()
    assert checker_a_info.get('activated') == CHECKER_A_SWITCH

    checker_b_info = application.checkers[CHECKER_B_FILENAME].json()
    assert checker_b_info.get('activated') == CHECKER_B_SWITCH


def test_activate_deactivate(event_server, checker_server):
    application.checkers[CHECKER_A_FILENAME].activate()
    assert application.checkers[CHECKER_A_FILENAME].activated == True

    application.checkers[CHECKER_A_FILENAME].deactivate()
    assert application.checkers[CHECKER_A_FILENAME].activated == False
