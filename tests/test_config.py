import pytest
from lyrebird import config
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


def test_create(tmpdir):
    custom_config = {"myconf": "myval"}
    conf_path = Path(tmpdir) / 'conf.json'
    with codecs.open(conf_path, 'w', 'utf-8') as f:
        f.write(json.dumps(custom_config, indent=4, ensure_ascii=False))
    cm = config.ConfigManager(conf_path=conf_path)
    assert str(cm.conf_file) == str(tmpdir) + '/conf.json'
    assert cm.conf_file.exists()
    assert cm.config
    assert cm.config['myconf'] == 'myval'


def test_override_config_with_forbidden_modify_field():
    cm = config.ConfigManager()
    cm.config = conf

    update_conf = {'ip': 'aaa', 'key1': 'value1'}

    with pytest.raises(config.ConfigException) as e:
        cm.override_config_field(update_conf)
    exec_msg = e.value.args[0]
    assert 'Config field cannot be modified' in exec_msg


def test_override_config_with_none():
    cm = config.ConfigManager()
    cm.config = copy.deepcopy(conf)
    cm.override_config_field(None)
    assert cm.config == conf


def test_override_config_with_empty_dict():
    cm = config.ConfigManager()
    cm.config = copy.deepcopy(conf)
    cm.override_config_field({})
    assert cm.config == conf


def test_override_config_with_normal():
    cm = config.ConfigManager()
    cm.config = copy.deepcopy(conf)
    cm.override_config_field({'key1': 'value1'})
    assert cm.config.get('key1') == 'value1'
    cm.override_config_field({'key1': 'value2'})
    assert cm.config.get('key1') == 'value2'
