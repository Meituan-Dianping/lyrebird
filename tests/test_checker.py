import pytest
from lyrebird.event import EventServer
from lyrebird import application
from lyrebird.checker import LyrebirdCheckerServer

CHECKER_A_FILENAME = "checker_a.py"
CHECKER_B_FILENAME = "checker_b.py"
CHECKER_C_FILENAME = "checker_c.py"
CHECKER_A_SWITCH = True
CHECKER_B_SWITCH = False
CHECKER_C_SWITCH = True

CONTENT = u"from lyrebird import event\n@event('flow')\ndef test_func():\n\tpass"

@pytest.fixture
def checker_init(tmp_path, tmpdir):
    # default config
    config = {
        "checker.workspace": tmp_path,
        "checker.switch": {
            CHECKER_A_FILENAME: CHECKER_A_SWITCH,
            CHECKER_B_FILENAME: CHECKER_B_SWITCH,
            CHECKER_C_FILENAME: CHECKER_C_SWITCH
        }
    }

    # init file dir
    checker_a_file = tmp_path / CHECKER_A_FILENAME
    checker_a_file.write_text(CONTENT)
    checker_b_file = tmp_path / CHECKER_B_FILENAME
    checker_b_file.write_text(CONTENT)
    checker_c_file = tmp_path / CHECKER_C_FILENAME
    checker_c_file.write_text(CONTENT)

    # mock config
    application._cm = type('MockedContentManager', (), {'config': config, 'root':tmpdir, 'ROOT':tmpdir})()

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
    server = EventServer()
    application.server['event'] = server
    yield server


def test_rank_valid(event_server, checker_server):
    new_content = u'''
from lyrebird import on_request, on_response, on_request_upstream, on_response_upstream, encoder, decoder

@on_request(rules={}, rank=1)
def test_func(flow):
    pass

@on_response(rules={}, rank=1)
def test_func(flow):
    pass

@on_request_upstream(rules={}, rank=1)
def test_func(flow):
    pass

@on_response_upstream(rules={}, rank=1)
def test_func(flow):
    pass

@encoder(rules={}, rank=1)
def test_func(flow):
    pass

@decoder(rules={}, rank=1)
def test_func(flow):
    pass
    '''
    application.checkers[CHECKER_C_FILENAME].write(new_content)
    assert application.on_request[0]['rank'] == 1
    assert application.on_response[0]['rank'] == 1
    assert application.on_request_upstream[0]['rank'] == 1
    assert application.on_response_upstream[0]['rank'] == 1
    assert application.encoder[0]['rank'] == 1
    assert application.decoder[0]['rank'] == 1
    application.checkers[CHECKER_C_FILENAME].deactivate()


def test_rank_invalid(event_server, checker_server):
    new_content = u'''
from lyrebird import on_request, on_response, on_request_upstream, on_response_upstream, encoder, decoder

@on_request(rules={}, rank='s')
def test_func(flow):
    pass

@on_response(rules={}, rank='s')
def test_func(flow):
    pass

@on_request_upstream(rules={}, rank='s')
def test_func(flow):
    pass

@on_response_upstream(rules={}, rank='s')
def test_func(flow):
    pass

@encoder(rules={}, rank='s')
def test_func(flow):
    pass

@decoder(rules={}, rank='s')
def test_func(flow):
    pass
    '''
    application.checkers[CHECKER_C_FILENAME].write(new_content)
    assert application.on_request[0]['rank'] == 0
    assert application.on_response[0]['rank'] == 0
    assert application.on_request_upstream[0]['rank'] == 0
    assert application.on_response_upstream[0]['rank'] == 0
    assert application.encoder[0]['rank'] == 0
    assert application.decoder[0]['rank'] == 0
    application.checkers[CHECKER_C_FILENAME].deactivate()


def test_rule_rank_default(event_server, checker_server):
    new_content = u'''
from lyrebird import on_request, on_response, on_request_upstream, on_response_upstream, encoder, decoder

@on_request()
def test_func(flow):
    pass

@on_response()
def test_func(flow):
    pass

@on_request_upstream()
def test_func(flow):
    pass

@on_response_upstream()
def test_func(flow):
    pass

@encoder()
def test_func(flow):
    pass

@decoder()
def test_func(flow):
    pass
    '''
    application.checkers[CHECKER_C_FILENAME].write(new_content)
    assert application.on_request[0]['rules'] == None
    assert application.on_response[0]['rules'] == None
    assert application.on_request_upstream[0]['rules'] == None
    assert application.on_response_upstream[0]['rules'] == None
    assert application.encoder[0]['rules'] == None
    assert application.decoder[0]['rules'] == None
    assert application.on_request[0]['rank'] == 0
    assert application.on_response[0]['rank'] == 0
    assert application.on_request_upstream[0]['rank'] == 0
    assert application.on_response_upstream[0]['rank'] == 0
    assert application.encoder[0]['rank'] == 0
    assert application.decoder[0]['rank'] == 0
    application.checkers[CHECKER_C_FILENAME].deactivate()


def test_load_checkers(event_server, checker_server):
    assert CHECKER_A_FILENAME in application.checkers
    assert len(application.checkers) == 3

    checker_a_info = application.checkers[CHECKER_A_FILENAME].json()
    assert checker_a_info.get('activated') == CHECKER_A_SWITCH

    checker_b_info = application.checkers[CHECKER_B_FILENAME].json()
    assert checker_b_info.get('activated') == CHECKER_B_SWITCH


def test_activate_deactivate(event_server, checker_server):
    application.checkers[CHECKER_A_FILENAME].activate()
    assert application.checkers[CHECKER_A_FILENAME].activated == True

    application.checkers[CHECKER_A_FILENAME].deactivate()
    assert application.checkers[CHECKER_A_FILENAME].activated == False


def test_read(event_server, checker_server):
    content = application.checkers[CHECKER_A_FILENAME].read()
    assert content == CONTENT


def test_wrtie_activated_checker(event_server, checker_server):
    new_content = u"from lyrebird import event\n@event('flow')\ndef test_func():\n\tprint('hello checker')"
    application.checkers[CHECKER_A_FILENAME].write(new_content)

    content = application.checkers[CHECKER_A_FILENAME].read()
    assert content == new_content

    checker_a_info = application.checkers[CHECKER_A_FILENAME].json()
    assert checker_a_info.get('activated') == CHECKER_A_SWITCH


def test_wrtie_inactivated_checker(event_server, checker_server):
    new_content = u"from lyrebird import event\n@event('flow')\ndef test_func():\n\tprint('hello checker')"
    application.checkers[CHECKER_B_FILENAME].write(new_content)

    content = application.checkers[CHECKER_B_FILENAME].read()
    assert content == new_content

    checker_b_info = application.checkers[CHECKER_B_FILENAME].json()
    assert checker_b_info.get('activated') == CHECKER_B_SWITCH
