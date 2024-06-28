import uuid
import traceback
from datetime import datetime
from urllib.parse import urlparse
from collections import OrderedDict
from copy import deepcopy

from lyrebird.log import get_logger
from lyrebird.mock.dm.match import MatchRules
from lyrebird.utils import flow_data_2_str, render


logger = get_logger()


class TempMock:
    def __init__(self):
        self.root = {
            'id': 'tmp_group',
            'type': 'group',
            'name': 'Temp Mock',
            'label': [],
            'children': []
        }
        self.activated_data = OrderedDict()

    def get(self):
        return self.root
    
    def get_matched_data(self, flow):
        _matched_data = []
        for data in self.activated_data.values():
            if MatchRules.match(flow, data.get('rule')):
                _matched_data.append(deepcopy(data))
                break

        for response_data in _matched_data:
            if 'response' not in response_data:
                continue
            if 'data' not in response_data['response']:
                continue
            if not response_data['response']['data']:
                continue

            origin_response_data = response_data['response']['data']
            try:
                response_data['response']['data'] = render(response_data['response']['data'])
            except Exception:
                response_data['response']['data'] = origin_response_data
                logger.warning(f'Format response data error! {response_data["request"]["url"]}\n {traceback.format_exc()}')

        return _matched_data

    def add_data(self, raw_data):
        if not isinstance(raw_data, dict):
            raise DataObjectShouldBeADict

        data = dict(raw_data)
        data_id = str(uuid.uuid4())
        data['id'] = data_id

        if 'request' in data:
            data['request'] = dict(raw_data['request'])

            _data_name = data['name'] if data.get('name') else self._get_data_name(data)
            _data_rule = data['rule'] if data.get('rule') else self._get_data_rule(data['request'])
            if 'data' in data['request']:
                data['request']['data'] = flow_data_2_str(data['request']['data'])
        else:
            _data_name = data.get('name')
            _data_rule = {'request.url': '(?=.*YOUR-REQUEST-PATH)(?=.*PARAMS)'}
            data['request'] = {}

        data['name'] = _data_name
        data['rule'] = _data_rule

        if 'response' in data:
            data['response'] = dict(raw_data['response'])

            if 'data' in data['response']:
                data['response']['data'] = flow_data_2_str(data['response']['data'])
        else:
            data['response'] = {}

        self.activated_data[data_id] = data
        self.activated_data.move_to_end(data_id, last=False)

        data_node = {
            'id': data_id,
            'name': data.get('name'),
            'type': 'data',
            'parent_id': 'tmp_group'
        }
        self.root['children'].insert(0, data_node)

        return data_id

    def delete_by_query(self, query):
        if not query.get('id'):
            return
        ids = query['id']

        for id_ in ids:
            if id_ in self.activated_data:
                del self.activated_data[id_]

        for child in self.root['children'][::-1]:
            if child['id'] in ids:
                self.root['children'].remove(child)

    @staticmethod
    def _get_data_name(data):
        name = 'New Data'
        request = data.get('request')
        if not request:
            return name

        url = request.get('url')
        if not url:
            return name

        parsed_url = urlparse(url)
        host = parsed_url.hostname
        path = parsed_url.path
        if path:
            name = path
        elif host:
            name = host
        else:
            name = url[0:100]

        time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        name = f'{time_now}  {name}'

        return name

    @staticmethod
    def _get_data_rule(request):
        pattern = 'YOUR-REQUEST-PATH'
        url = request.get('url')
        if not url:
            return {'request.url': f'(?=.*{pattern})'}

        parsed_url = urlparse(url)
        host = parsed_url.netloc
        path = parsed_url.path
        query = parsed_url.query
        if path and host:
            pattern = path
            if query:
                pattern += '\?' 
            elif url.endswith(path):
                pattern += '$'

        elif host:
            pattern = host
            if url.endswith(host):
                pattern += '$'

        else:
            pattern = url
        return {'request.url': f'(?=.*{pattern})'}


class DataObjectShouldBeADict(Exception):
    pass
