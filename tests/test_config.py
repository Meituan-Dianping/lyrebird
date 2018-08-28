from lyrebird import config
from pathlib import Path
import json
import codecs


def test_create(tmpdir):
    custom_config = {"myconf":"myval"}
    conf_path = Path(tmpdir)/'conf.json'
    with codecs.open(conf_path, 'w', 'utf-8') as f:
        f.write(json.dumps(custom_config, indent=4, ensure_ascii=False))
    cm = config.ConfigManager(conf_path=conf_path)
    assert str(cm.conf_file) == str(tmpdir) + '/conf.json'
    assert cm.conf_file.exists()
    assert cm.config
    assert cm.config['myconf'] == 'myval'
