import json
import codecs
import uuid
from pathlib import Path
import shutil
from urllib.parse import urlparse
from .exceptions import DataNotExistsError, DataIsNotDirError, DataInfoNotFoundError
from .data_file import DataFile


class Data:
    """
    Test data

    
    """

    info_filename = '.lyrebird_prop'

    def __init__(self, data_id, data_name, data_path, data_rule=None):
        self.id = data_id
        self.name = data_name
        self.path = data_path
        self.rule = data_rule

        self.request = DataFile(self, 'request', filetype='json')
        self.request_data = DataFile(self, 'request_data')
        self.response = DataFile(self, 'response', filetype='json')
        self.response_data = DataFile(self, 'response_data')


    @classmethod
    def createify(cls, data_path):
        new_path = Path(data_path)
        if not new_path.exists():
            raise DataNotExistsError(data_path)
        if not new_path.is_dir():
            raise DataIsNotDirError(data_path)
        # Read data info
        with codecs.open(new_path/cls.info_filename, 'r' , 'utf-8') as f:
            info = json.load(f)
        if not info:
            raise DataInfoNotFoundError(new_path)
        
        _id = info.get('id')
        _name = info.get('name')
        _rule = info.get('rule')
        return cls(_id, _name, new_path, _rule)

    @classmethod
    def new_data(cls, data_dir, flow=None, request=None, request_data=None, response=None, response_data=None):
        _id = str(uuid.uuid4())
        _name = _id

        _url = None
        if flow:
            _url = flow.get('request', {'url': None}).get('url')
        elif request:
            _req = json.loads(request)
            _url = request.get('url')
        
        _rule = {'request.url':None}

        if _url:
            parsed_url = urlparse(_url)
            if parsed_url.path is not '':
                _name = parsed_url.path
            else:
                _name = parsed_url.hostname
            _rule['request.url'] = f'(?=.*{_name})'

        _data_path = Path(data_dir)/_id
        _data_path.mkdir(parents=True, exist_ok=True)

        data = cls(_id, _name, _data_path)
        
        data.rule = _rule

        if flow:
            data.set_flow(flow)
        else:
            data.request.content = request
            data.request_data.content = request_data
            data.response.content = response
            data.response_data.content = response_data
        return data

    def set_flow(self, flow):
        if flow.get('request'):
            request_obj = {
                'method': flow['request'].get('method'),
                'url': flow['request'].get('url'),
                'headers': flow['request'].get('headers')
            }
            content_type = request_obj['headers'].get('Content-Type')
            if content_type and 'json' in content_type:
                self.request_data.filetype = 'json'
            elif content_type and 'html' in content_type:
                self.request_data.filetype = 'html'
            elif content_type and 'xml' in content_type:
                self.request_data.filetype = 'xml'
            elif content_type and 'text' in content_type:
                self.request_data.filetype = 'text'

            self.request.content = json.dumps(request_obj, ensure_ascii=False, indent=4)
            if flow['request'].get('data'):
                self.request_data.content = flow['request'].get('data')

        if flow.get('response'):
            response_obj = {
                'code': flow['response'].get('code'),
                'headers': flow['response'].get('headers')
            }
            content_type = response_obj['headers'].get('Content-Type')
            if content_type and 'json' in content_type:
                self.response_data.filetype = 'json'
            elif content_type and 'html' in content_type:
                self.response_data.filetype = 'html'
            elif content_type and 'xml' in content_type:
                self.response_data.filetype = 'xml'
            elif content_type and 'text' in content_type:
                self.response_data.filetype = 'text'
            
            self.response.content = json.dumps(response_obj, ensure_ascii=False, indent=4)
            if flow['response'].get('data'):
                if self.response_data.filetype == 'json':
                    self.response_data.content = json.dumps(flow['response'].get('data'))
                else:
                    self.response_data.content = flow['response'].get('data')


    def save(self):
        with codecs.open(self.path/self.info_filename, 'w', 'utf-8') as f:
            info = {
                'id': self.id,
                'name': self.name,
                'rule': self.rule,
                'data_files': {
                    'request': {
                        'filetype': self.request.filetype
                    },
                    'request_data': {
                        'filetype': self.request_data.filetype
                    },
                    'response':{
                        'filetype': self.response.filetype
                    },
                    'response_data': {
                        'filetype': self.response_data.filetype
                    }
                }
            }
            if self.request.content:
                info['url'] = json.loads(self.request.content).get('url')
            json.dump(info, f, ensure_ascii=False, indent=4)

    
    def delete(self):
        shutil.rmtree(self.path)

    def _get_content_type_from_content(self, content):
        filetype = 'bin'
        content_obj = json.loads(content)
        content_type = content_obj.get('headers', {}).get('Content-Type')
        if content_type and 'json' in content_type:
            filetype = 'json'
        elif content_type and 'html' in content_type:
            filetype = 'html'
        elif content_type and 'xml' in content_type:
            filetype = 'xml'
        elif content_type and 'text' in content_type:
            filetype = 'text'
        return filetype

    def json(self, detail=False):
        json_obj = {
            'id': self.id,
            'name': self.name
        }
        if detail:
            json_obj['rule'] = self.rule
            if self.request.content:
                json_obj['request'] = self.request.json()
                self.request_data.filetype = self._get_content_type_from_content(self.request.content)
            if self.request_data.content:
                json_obj['request_data'] = self.request_data.json()
            if self.response.content:
                json_obj['response'] = self.response.json()
            if self.response_data.content:
                self.response_data.filetype = self._get_content_type_from_content(self.response.content)
                json_obj['response_data'] = self.response_data.json()
        return json_obj
