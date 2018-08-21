from lyrebird import nconfig
from pathlib import Path


def test_create(tmpdir):
    cm = nconfig.ConfigManager(conf_root_path=tmpdir)
    assert str(cm.conf_path) == str(tmpdir) + '/conf.json'
    assert cm.conf_path.exists()
    assert cm.config
    assert cm.config == nconfig.config_template
