import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time



current_path = os.path.abspath(os.path.dirname(__file__))
checker_path = f'{current_path}/assets/checker.py'
modifier_path = f'{current_path}/assets/flow_editor.py'
REQUEST_NUM = 60
AVU_DURATION = 2
ALL_DURATION = 15


def fetch_url(req_url):
    response = requests.get(req_url)
    return response.text


def send_request(url):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(fetch_url, url) for i in range(REQUEST_NUM)]
        for future in as_completed(futures):
            try:
                res = future.result()
            except Exception as e:
                print(f"Request Error:{e}")


def test_performance(lyrebird, mock_server):
    start_time = time.time()
    send_request(lyrebird.uri_mock + mock_server.api_long_time_service)
    end_time = time.time()
    duration = end_time - start_time
    r = requests.get(url=lyrebird.api_flows).json()
    sum_time = sum(flow['duration'] for flow in r)
    assert len(r) == REQUEST_NUM
    assert sum_time/len(r) < AVU_DURATION
    assert duration < ALL_DURATION
    lyrebird.stop()


def test_performance_with_checker(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=[checker_path])
    start_time = time.time()
    send_request(lyrebird_with_args.uri_mock + mock_server.api_long_time_service)
    end_time = time.time()
    duration = end_time - start_time
    r = requests.get(url=lyrebird_with_args.api_flows).json()
    sum_time = sum(flow['duration'] for flow in r)
    assert len(r) == REQUEST_NUM
    assert sum_time/len(r) < AVU_DURATION
    assert duration < ALL_DURATION
    lyrebird_with_args.stop()


def test_performance_with_modifier(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=[modifier_path])
    start_time = time.time()
    send_request(lyrebird_with_args.uri_mock + mock_server.api_long_time_service)
    end_time = time.time()
    duration = end_time - start_time
    r = requests.get(url=lyrebird_with_args.api_flows).json()
    sum_time = sum(flow['duration'] for flow in r)
    assert len(r) == REQUEST_NUM
    assert sum_time/len(r) < AVU_DURATION
    assert duration < ALL_DURATION
    lyrebird_with_args.stop()


def test_performance_with_checker_and_modifier(lyrebird_with_args, mock_server):
    lyrebird_with_args.start(checker_path=[checker_path, modifier_path])
    start_time = time.time()
    send_request(lyrebird_with_args.uri_mock + mock_server.api_long_time_service)
    end_time = time.time()
    duration = end_time - start_time
    r = requests.get(url=lyrebird_with_args.api_flows).json()
    sum_time = sum(flow['duration'] for flow in r)
    assert len(r) == REQUEST_NUM
    assert sum_time/len(r) < AVU_DURATION
    assert duration < ALL_DURATION
    lyrebird_with_args.stop()
