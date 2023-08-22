import pytest
from copy import deepcopy
from lyrebird.event import EventServer
from lyrebird import application
from lyrebird.checker import LyrebirdCheckerServer
from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder


FILENAME = 'encoder_decoder.py'

CONTENT = u'''
from lyrebird import encoder, decoder

@encoder(rules={'request.url': 'meituan'})
def test_func(flow):
    flow['request']['data'] = 'encode'

@decoder(rules={'request.url': 'meituan'})
def test_func(flow):
    flow['request']['data'] = 'decode'
    '''


FLOW_DATA_MATCH = {
        'request': {
            'url': 'http://www.meituan.com',
            'data': ''
        }
    }

FLOW_DATA_NO_MATCH = {
        'request': {
            'url': 'http://www.bing.com',
            'data': ''
        }
    }

@pytest.fixture
def checker_init(tmp_path, tmpdir):
    # default config
    config = {
        'checker.workspace': tmp_path,
        'checker.switch': {
            FILENAME: True
        }
    }

    # init file dir

    encoder_decoder_file = tmp_path / FILENAME
    encoder_decoder_file.write_text(CONTENT)

    # mock config
    application._cm = type('MockedContentManager', (), {'config': config, 'root':tmpdir, 'ROOT':tmpdir})()

    return application.checkers

@pytest.fixture
def checker_server(checker_init, tmp_path):
    server = LyrebirdCheckerServer()
    server.start()
    server.SCRIPTS_DIR = tmp_path
    application.server['checker'] = server
    application.encoders_decoders = EncoderDecoder()
    yield server
    server.stop()


@pytest.fixture
def event_server():
    server = EventServer()
    application.server['event'] = server
    yield server


def test_encoder_handler_match_and_no_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_MATCH)
    application.encoders_decoders.encoder_handler(flow)
    assert flow['request']['data'] == 'encode'


def test_encoder_handler_not_match_and_no_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_NO_MATCH)
    application.encoders_decoders.encoder_handler(flow)
    assert flow['request']['data'] == ''


def test_encoder_handler_match_and_exist_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_MATCH)
    output = {}
    application.encoders_decoders.encoder_handler(flow, output)
    assert flow['request']['data'] == ''
    assert output['request']['data'] == 'encode'
    output['request']['data'] == 'test'
    assert flow['request']['data'] == ''


def test_encoder_handler_not_match_and_exist_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_NO_MATCH)
    output = {}
    application.encoders_decoders.encoder_handler(flow, output)
    assert flow['request']['data'] == ''
    assert output['request']['data'] == ''
    output['request']['data'] == 'test'
    assert flow['request']['data'] == ''


def test_decoder_handler_match_and_no_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_MATCH)
    application.encoders_decoders.decoder_handler(flow)
    assert flow['request']['data'] == 'decode'


def test_decoder_handler_not_match_and_no_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_NO_MATCH)
    application.encoders_decoders.decoder_handler(flow)
    assert flow['request']['data'] == ''


def test_decoder_handler_match_and_exist_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_MATCH)
    output = {}
    application.encoders_decoders.decoder_handler(flow, output)
    assert flow['request']['data'] == ''
    assert output['request']['data'] == 'decode'
    output['request']['data'] == 'test'
    assert flow['request']['data'] == ''


def test_decoder_handler_not_match_and_exist_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_NO_MATCH)
    output = {}
    application.encoders_decoders.decoder_handler(flow, output)
    assert flow['request']['data'] == ''
    assert output['request']['data'] == ''
    output['request']['data'] == 'test'
    assert flow['request']['data'] == ''
