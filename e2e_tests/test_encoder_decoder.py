import os
import requests
from urllib.parse import quote

extension_path = os.path.abspath(os.path.dirname(__file__)) + '/assets/encoder_decoder.py'
test_word = "你好,世界!Hello,world!"

def test_api_flow_decode(lyrebird, mock_server):
    url_ori = mock_server.api_status + f'?param={test_word}'
    url_encode = mock_server.api_status + f'?param={quote(test_word)}'
    requests.get(url=lyrebird.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird.uri_flow + f'/{request_id}?no_decode=0').json()
    param = r['data']['request']['query']['param']
    url = r['data']['request']['url']
    assert param == test_word
    assert url == url_ori


def test_api_flow_not_decode(lyrebird, mock_server):
    url_encode = mock_server.api_status + f'?param={quote(test_word)}'
    requests.get(url=lyrebird.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird.uri_flow + f'/{request_id}?no_decode=1').json()
    param = r['data']['request']['query']['param']
    url = r['data']['request']['url']
    assert param == quote(test_word)
    assert url == url_encode


def test_api_flow_default_not_decode(lyrebird, mock_server):
    url_ori = mock_server.api_status + f'?param={test_word}'
    url_encode = mock_server.api_status + f'?param={quote(test_word)}'
    requests.get(url=lyrebird.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird.uri_flow + f'/{request_id}').json()
    param = r['data']['request']['query']['param']
    url = r['data']['request']['url']
    assert param == test_word
    assert url == url_ori


def test_api_flow_ori(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=extension_path)
    url_encode = mock_server.api_status + f'?encoder_decoder_param={quote(test_word)}'
    requests.get(url=lyrebird_with_args.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird_with_args.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird_with_args.uri_flow + f'/{request_id}?is_origin=true').json()
    header = r['data']['request']['headers'].get('test_encoder_decoder','')
    assert header == ''


def test_api_flow_not_ori(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=extension_path)
    url_encode = mock_server.api_status + f'?encoder_decoder_param={quote(test_word)}'
    requests.get(url=lyrebird_with_args.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird_with_args.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird_with_args.uri_flow + f'/{request_id}?is_origin=false').json()
    header = r['data']['request']['headers'].get('test_encoder_decoder','')
    assert header == 'decode'


def test_api_flow_ori_capital(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=extension_path)
    url_encode = mock_server.api_status + f'?encoder_decoder_param={quote(test_word)}'
    requests.get(url=lyrebird_with_args.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird_with_args.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird_with_args.uri_flow + f'/{request_id}?is_origin=True').json()
    header = r['data']['request']['headers'].get('test_encoder_decoder','')
    assert header == ''


def test_api_flow_not_ori_capital(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=extension_path)
    url_encode = mock_server.api_status + f'?encoder_decoder_param={quote(test_word)}'
    requests.get(url=lyrebird_with_args.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird_with_args.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird_with_args.uri_flow + f'/{request_id}?is_origin=FALSE').json()
    header = r['data']['request']['headers'].get('test_encoder_decoder','')
    assert header == 'decode'


def test_api_flow_default_not_ori(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=extension_path)
    url_encode = mock_server.api_status + f'?encoder_decoder_param={quote(test_word)}'
    requests.get(url=lyrebird_with_args.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird_with_args.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird_with_args.uri_flow + f'/{request_id}').json()
    header = r['data']['request']['headers'].get('test_encoder_decoder','')
    assert header == 'decode'


def test_api_flow_not_decode_and_ori(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=extension_path)
    url_encode = mock_server.api_status + f'?encoder_decoder_param={quote(test_word)}'
    requests.get(url=lyrebird_with_args.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird_with_args.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird_with_args.uri_flow + f'/{request_id}?is_origin=true&no_decode=1').json()
    param = r['data']['request']['query']['encoder_decoder_param']
    url = r['data']['request']['url']
    header = r['data']['request']['headers'].get('test_encoder_decoder','')
    assert param == quote(test_word)
    assert url == url_encode
    assert header == ''


def test_api_flow_decode_and_ori(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=extension_path)
    url_ori = mock_server.api_status + f'?encoder_decoder_param={test_word}'
    url_encode = mock_server.api_status + f'?encoder_decoder_param={quote(test_word)}'
    requests.get(url=lyrebird_with_args.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird_with_args.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird_with_args.uri_flow + f'/{request_id}?is_origin=true&no_decode=0').json()
    param = r['data']['request']['query']['encoder_decoder_param']
    url = r['data']['request']['url']
    header = r['data']['request']['headers'].get('test_encoder_decoder','')
    assert param == test_word
    assert url == url_ori
    assert header == ''


def test_api_flow_not_decode_and_not_ori(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=extension_path)
    url_encode = mock_server.api_status + f'?encoder_decoder_param={quote(test_word)}'
    requests.get(url=lyrebird_with_args.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird_with_args.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird_with_args.uri_flow + f'/{request_id}?is_origin=false&no_decode=1').json()
    param = r['data']['request']['query']['encoder_decoder_param']
    url = r['data']['request']['url']
    header = r['data']['request']['headers'].get('test_encoder_decoder','')
    assert param == quote(test_word)
    assert url == url_encode
    assert header == 'decode'


def test_api_flow_decode_and_not_ori(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=extension_path)
    url_ori = mock_server.api_status + f'?encoder_decoder_param={test_word}'
    url_encode = mock_server.api_status + f'?encoder_decoder_param={quote(test_word)}'
    requests.get(url=lyrebird_with_args.uri_mock + url_encode)
    request_id = requests.get(url=lyrebird_with_args.uri_flow).json()[0]['id']
    r = requests.get(url=lyrebird_with_args.uri_flow + f'/{request_id}?is_origin=false&no_decode=0').json()
    param = r['data']['request']['query']['encoder_decoder_param']
    url = r['data']['request']['url']
    header = r['data']['request']['headers'].get('test_encoder_decoder','')
    assert param == test_word
    assert url == url_ori
    assert header == 'decode'
