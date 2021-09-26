

from typing import NamedTuple
from lyrebird import application, reporter
from lyrebird.event import EventServer
from lyrebird.task import BackgroundTaskServer
from lyrebird.mock.mock_server import LyrebirdMockServer
from lyrebird.mock.handlers.encoder_decoder_handler import EncoderDecoder

import pytest
import json


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

MockConfigManager = NamedTuple('MockConfigManager', [('config', dict)])

@pytest.fixture
def client():
    application._cm = MockConfigManager(config=conf)
    application.server['event'] = EventServer()
    application.reporter = reporter.Reporter()
    application.server['task'] = BackgroundTaskServer()
    application.encoders_decoders = EncoderDecoder()
    server = LyrebirdMockServer()
    client = server.app.test_client()
    yield client


def test_patch_conf_api_with_no_param(client):
    before_conf = application.config.raw()
    resp = client.patch("/api/conf")
    after_conf = application.config.raw()
    assert 200 <= resp.status_code <= 400
    assert before_conf == after_conf
    

def test_patch_conf_api_with_custom_fields(client):

    # add new config field
    before_conf = application.config.raw()
    assert "custom.key1" not in before_conf
    assert "custom.key2" not in before_conf
    resp = client.patch("/api/conf", json={"custom.key1":"value1", "custom.key2":"value2"})
    assert 200 <= resp.status_code <= 400
    assert application.config.get("custom.key1") == "value1"
    assert application.config.get("custom.key2") == "value2"

    # update config field
    resp = client.patch("/api/conf", json={"custom.key1":"value3"})
    assert 200 <= resp.status_code <= 400
    assert application.config.get("custom.key1") == "value3"


def test_patch_conf_api_with_forbidden_field(client):

    before_conf = application.config.raw()
    resp = client.patch("/api/conf", json={"ip":"111111"})
    after_conf = application.config.raw()
    assert 200 <= resp.status_code <= 400
    assert before_conf == after_conf
    assert resp.json["code"] == 3000
    assert resp.json["message"] == "配置中{'ip'}字段禁止修改"
