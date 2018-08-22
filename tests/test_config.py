from lyrebird import config
from pathlib import Path


def test_create(tmpdir):
    cm = config.ConfigManager(conf_root_path=tmpdir)
    assert str(cm.conf_file) == str(tmpdir) + '/conf.json'
    assert cm.conf_file.exists()
    assert cm.config
    assert cm.config == config.config_template
