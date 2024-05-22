import re
import pytest
import codecs
import json
from copy import deepcopy
import lyrebird
from .utils import FakeSocketio, FakeEvnetServer
from lyrebird.mock import dm
from lyrebird.config import ConfigManager
from lyrebird.checker import LyrebirdCheckerServer
from lyrebird.config import CONFIG_TREE_SHOW_CONFIG
from lyrebird.mock.dm.file_data_adapter import data_adapter
from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder
from lyrebird import application


data_a = {
    'id': 'dataA-UUID',
    'name': 'dataA',
    'rule': {
        'request.url': '/api/search'
    },
    'request': {
        'url': 'http://unittest.com/api/search'
    }
}

data_b = {
    'id': 'dataB-UUID',
    'name': '.Settings',
    'json': '{\n    \"checker.switch\": {\n        \"checker_a.py\": true,\n        \"checker_b.py\": false\n    }\n}'
}


prop = {
    'id': 'root',
    'name': 'root',
    'type': 'group',
    'parent_id': None,
    'children': [
        {
            'id': 'groupA-UUID',
            'name': 'groupA',
            'type': 'group',
            'parent_id': 'root',
            'children': [
                {
                    'id': 'dataA-UUID',
                    'name': 'dataA',
                    'type': 'data',
                    'parent_id': 'groupA-UUID'
                },
                {
                    'id': 'dataB-UUID',
                    'name': '.Settings',
                    'type': 'config',
                    'parent_id': 'groupA-UUID'
                },
            ]
        },
        {
            'id': 'groupB-UUID',
            'name': 'groupC',
            'type': 'group',
            'parent_id': 'root',
            'children': []
        }
    ]
}


@pytest.fixture
def root(tmpdir):
    with codecs.open(tmpdir / 'dataA-UUID', 'w') as f:
        json.dump(data_a, f)
    with codecs.open(tmpdir / 'dataB-UUID', 'w') as f:
        json.dump(data_b, f)
    with codecs.open(tmpdir / '.lyrebird_prop', 'w') as f:
        json.dump(prop, f)
    return tmpdir


@pytest.fixture
def data_manager(root, tmpdir):
    application._cm = ConfigManager()
    lyrebird.mock.context.application.socket_io = FakeSocketio()
    application.encoders_decoders = EncoderDecoder()
    _dm = dm.DataManagerV2()
    _dm.snapshot_workspace = tmpdir
    _dm.set_adapter(data_adapter)
    _dm.set_root(root)
    yield _dm
    del _dm


CHECKER_A_FILENAME = 'checker_a.py'
CHECKER_B_FILENAME = 'checker_b.py'
CHECKER_A_SWITCH = False
CHECKER_B_SWITCH = True

CONTENT = u"from lyrebird import event\n@event('flow')\ndef test_func():\n\tpass"

@pytest.fixture
def checker_init(tmp_path, tmpdir):
    config = {
        'checker.workspace': tmp_path,
        'checker.switch': {
            CHECKER_A_FILENAME: CHECKER_A_SWITCH,
            CHECKER_B_FILENAME: CHECKER_B_SWITCH
        }
    }

    checker_a_file = tmp_path / CHECKER_A_FILENAME
    checker_a_file.write_text(CONTENT)
    checker_b_file = tmp_path / CHECKER_B_FILENAME
    checker_b_file.write_text(CONTENT)

    application._cm.config.update(config)

    return application.checkers

@pytest.fixture
def checker_server(checker_init, tmp_path):
    server = LyrebirdCheckerServer()
    server.start()
    server.SCRIPTS_DIR = tmp_path
    application.server['checker'] = server
    yield server
    server.stop()
    del server


@pytest.fixture
def event_server():
    application.server['event'] = FakeEvnetServer()
    yield None

def test_activate_with_config_contains_extension(data_manager, event_server, checker_server):
    assert application.checkers[CHECKER_A_FILENAME].activated  == False
    assert application.checkers[CHECKER_B_FILENAME].activated == True
    data_manager.activate('groupA-UUID')

    assert application.checkers[CHECKER_A_FILENAME].activated  == True
    assert application.checkers[CHECKER_B_FILENAME].activated == False
