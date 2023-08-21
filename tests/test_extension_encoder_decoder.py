import pytest
from copy import deepcopy
from lyrebird.event import EventServer
from lyrebird import application
from lyrebird.checker import LyrebirdCheckerServer
from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder


ENCODER_FILENAME = 'test_encoder.py'
DECODER_FILENAME = 'test_decoder.py'

ENCODER_CONTENT = u'''
from lyrebird import encoder, decoder

@encoder(rules={'request.url': 'meituan'})
def test_func(flow):
    flow['request']['data'] = 'encode'
    '''

DECODER_CONTENT = u'''
from lyrebird import encoder, decoder

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
            ENCODER_FILENAME: False,
            DECODER_FILENAME: False
        }
    }

    # init file dir

    encoder_file = tmp_path / ENCODER_FILENAME
    encoder_file.write_text(ENCODER_CONTENT)
    decoder_file = tmp_path / DECODER_FILENAME
    decoder_file.write_text(DECODER_CONTENT)

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
    application.checkers[ENCODER_FILENAME].activate()
    application.encoders_decoders = EncoderDecoder()
    application.encoders_decoders.encoder_handler(flow)
    assert flow['request']['data'] == 'encode'
    application.checkers[ENCODER_FILENAME].deactivate()


def test_encoder_handler_not_match_and_no_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_NO_MATCH)
    application.checkers[ENCODER_FILENAME].activate()
    application.encoders_decoders = EncoderDecoder()
    application.encoders_decoders.encoder_handler(flow)
    assert flow['request']['data'] == ''
    application.checkers[ENCODER_FILENAME].deactivate()


def test_encoder_handler_match_and_exist_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_MATCH)
    output = {}
    application.checkers[ENCODER_FILENAME].activate()
    application.encoders_decoders = EncoderDecoder()
    application.encoders_decoders.encoder_handler(flow, output)
    assert flow['request']['data'] == ''
    assert output['request']['data'] == 'encode'
    output['request']['data'] == 'test'
    assert flow['request']['data'] == ''
    application.checkers[ENCODER_FILENAME].deactivate()


def test_encoder_handler_not_match_and_exist_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_NO_MATCH)
    output = {}
    application.checkers[ENCODER_FILENAME].activate()
    application.encoders_decoders = EncoderDecoder()
    application.encoders_decoders.encoder_handler(flow, output)
    assert flow['request']['data'] == ''
    assert output['request']['data'] == ''
    output['request']['data'] == 'test'
    assert flow['request']['data'] == ''
    application.checkers[ENCODER_FILENAME].deactivate()


def test_decoder_handler_match_and_no_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_MATCH)
    application.checkers[DECODER_FILENAME].activate()
    application.encoders_decoders = EncoderDecoder()
    application.encoders_decoders.decoder_handler(flow)
    assert flow['request']['data'] == 'decode'
    application.checkers[DECODER_FILENAME].deactivate()


def test_decoder_handler_not_match_and_no_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_NO_MATCH)
    application.checkers[DECODER_FILENAME].activate()
    application.encoders_decoders = EncoderDecoder()
    application.encoders_decoders.decoder_handler(flow)
    assert flow['request']['data'] == ''
    application.checkers[DECODER_FILENAME].deactivate()


def test_decoder_handler_match_and_exist_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_MATCH)
    output = {}
    application.checkers[DECODER_FILENAME].activate()
    application.encoders_decoders = EncoderDecoder()
    application.encoders_decoders.decoder_handler(flow, output)
    assert flow['request']['data'] == ''
    assert output['request']['data'] == 'decode'
    output['request']['data'] == 'test'
    assert flow['request']['data'] == ''
    application.checkers[DECODER_FILENAME].deactivate()


def test_decoder_handler_not_match_and_exist_output(event_server, checker_server):
    flow = deepcopy(FLOW_DATA_NO_MATCH)
    output = {}
    application.checkers[DECODER_FILENAME].activate()
    application.encoders_decoders = EncoderDecoder()
    application.encoders_decoders.decoder_handler(flow, output)
    assert flow['request']['data'] == ''
    assert output['request']['data'] == ''
    output['request']['data'] == 'test'
    assert flow['request']['data'] == ''
    application.checkers[DECODER_FILENAME].deactivate()
