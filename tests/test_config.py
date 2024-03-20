import pytest
from lyrebird import config, application, reporter
from lyrebird.task import BackgroundTaskServer
from pathlib import Path
import json
import codecs
import copy

conf = {
    "version": "0.10.4",
    "proxy.filters": ["kuxun", "meituan", "sankuai", "dianping"],
    "proxy.port": 4272,
    "mock.port": 9090,
    "ip": "127.0.0.1",
    "mock.data": "data",
    "mock.proxy_headers": {
        "scheme": "MKScheme",
        "host": "MKOriginHost",
        "port": "MKOriginPort"
    }
}

@pytest.fixture
def cm():
    cm = config.ConfigManager()
    application._cm = cm
    application.sync_manager = application.SyncManager()
    application.server['task'] = BackgroundTaskServer()
    application.reporter = reporter.Reporter()
    yield cm


def test_create(tmpdir):
    custom_config = {"myconf": "myval"}
    conf_path = Path(tmpdir) / 'conf.json'
    with codecs.open(conf_path, 'w', 'utf-8') as f:
        f.write(json.dumps(custom_config, indent=4, ensure_ascii=False))
    cm = config.ConfigManager(conf_path_list=[conf_path])
    assert str(cm.conf_file) == str(tmpdir) + '/conf.json'
    assert cm.conf_file.exists()
    assert cm.config
    assert cm.config['myconf'] == 'myval'


def test_create_multiple_config(tmpdir):
    custom_config_1 = {'key_same': 'val_same_01', 'key_diff': 'val_diff'}
    conf_path_1 = Path(tmpdir) / 'conf_01.json'
    with codecs.open(conf_path_1, 'w', 'utf-8') as f:
        f.write(json.dumps(custom_config_1, indent=4, ensure_ascii=False))

    custom_config_2 = {'key_same': 'val_same_02'}
    conf_path_2 = Path(tmpdir) / 'conf_02.json'
    with codecs.open(conf_path_2, 'w', 'utf-8') as f:
        f.write(json.dumps(custom_config_2, indent=4, ensure_ascii=False))

    cm = config.ConfigManager(conf_path_list=[conf_path_1, conf_path_2])
    assert cm.config['key_same'] == 'val_same_02'
    assert cm.config['key_diff'] == 'val_diff'


def test_override_config_with_forbidden_modify_field(cm):
    cm.config = conf

    update_conf = {'version': '1.0.0', 'key1': 'value1'}

    with pytest.raises(config.ConfigException) as e:
        cm.override_config_field(update_conf)
    exec_msg = e.value.args[0]
    assert 'Config field cannot be modified' in exec_msg


def test_override_config_with_none(cm):
    cm.config = copy.deepcopy(conf)
    cm.override_config_field(None)
    assert cm.config == conf


def test_override_config_with_empty_dict(cm):
    cm.config = copy.deepcopy(conf)
    cm.override_config_field({})
    assert cm.config == conf


def test_override_config_with_normal(cm):
    cm.config = copy.deepcopy(conf)
    cm.override_config_field({'key1': 'value1'})
    assert cm.config.get('key1') == 'value1'
    cm.override_config_field({'key1': 'value2'})
    assert cm.config.get('key1') == 'value2'
