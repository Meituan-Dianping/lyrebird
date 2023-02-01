import re
import pytest
from lyrebird import application
from lyrebird.mock.dm import DataManager
from lyrebird.config import ConfigManager


@pytest.fixture
def config():
    _conf = {
        'ip': '127.0.0.1',
        'mock.port': 9090,
        'custom_key': 'custom_value',
        'config.value.tojsonKey': ['custom.[a-z0-9]{8}(-[a-z0-9]{4}){3}-[a-z0-9]{12}'],
        'custom.8df051be-4381-41b6-9252-120d9b558bf6': {"custom_key": "custom_value"}
    }
    application._cm = ConfigManager()
    application._cm.config = _conf


def test_format_ip(config):
    flow = {
        'response': {
            'data': '{{ip}}'
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert data == '127.0.0.1'


def test_format_port(config):
    flow = {
        'response': {
            'data': '{{port}}'
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert data == '9090'


def test_format_config(config):
    flow = {
        'response': {
            'data': "{{config.get('custom_key')}}"
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert data == 'custom_value'


def test_format_today(config):
    flow = {
        'response': {
            'data': '{{today}}'
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', data)


def test_format_today(config):
    flow = {
        'response': {
            'data': "{{now.strftime('%Y-%m-%d %H:%M:%S')}}"
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', data)


def test_format_tojson(config):
    flow = {
        'response': {
            'data': '"keyA":"valueA","keyB":"{{config.get(\'custom.8df051be-4381-41b6-9252-120d9b558bf6\')}}","keyC":"valueC"'
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert '"keyA":"valueA"' in data
    assert '"keyB":{"custom_key": "custom_value"}' in data
    assert '"keyC":"valueC"' in data



def test_format_no_param(config):
    response_data_str = 'ip'
    flow = {
        'response': {
            'data': response_data_str
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert data == response_data_str


def test_format_empty_parameter(config):
    response_data_str = '{{}}'
    flow = {
        'response': {
            'data': response_data_str
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert data == response_data_str


def test_format_with_mismatched_left_keyword(config):
    mismatched_str = ' ip {{ip {%ip {#ip'
    response_data_str = '{{ip}}' + mismatched_str
    flow = {
        'response': {
            'data': response_data_str
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert data == f'127.0.0.1{mismatched_str}'


def test_format_with_mismatched_right_keyword(config):
    response_data_str = ' ip ip}} }} ip%} ip#}'
    flow = {
        'response': {
            'data': response_data_str
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert data == response_data_str


def test_format_with_more_than_2_big_brackets(config):
    response_data_str = '{{{ ip }}} {{{{ ip }}}} {{% loop %}} {{# comment #}}'
    flow = {
        'response': {
            'data': response_data_str
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert data == response_data_str


def test_format_unknown_parameter(config):
    response_data_str = '{{unknown}} content {{unknown}} content {{unknown2}}'
    flow = {
        'response': {
            'data': response_data_str
        }
    }
    DataManager._format_respose_data(flow)
    data = flow['response']['data']
    assert data == response_data_str
