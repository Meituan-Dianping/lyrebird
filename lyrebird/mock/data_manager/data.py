import json
import codecs
import uuid
from pathlib import Path
from urllib.parse import urlparse
from .exceptions import DataNotExistsError, DataIsNotDirError, DataInfoNotFoundError
from .data_file import DataFile


class Data:
    """
    Test data

    
    """

    info_filename = '.info'

    def __init__(self, data_id, data_name, data_path, data_rule=None, flow=None):
        self.id = data_id
        self.name = data_name
        self.path = data_path
        self.rule = data_rule
        self.flow = flow

        self.request_data_type = 'json'
        self.response_data_type = 'json'

        self.request = DataFile(self, 'request')
        self.request_data = DataFile(self, 'request_data')
        self.response = DataFile(self, 'response')
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
    def new_data(cls, data_dir, flow):
        _id = str(uuid.uuid4())
        _name = _id

        _url = flow.get('request', {'url': None}).get('url')
        if _url:
            parsed_url = urlparse(_url)
            if parsed_url.path is not '':
                _name = parsed_url.path
            else:
                _name = parsed_url.hostname

        _data_path = Path(data_dir)/_id
        _data_path.mkdir(parents=True, exist_ok=True)

        data = cls(_id, _name, _data_path)
        if flow.get('request'):
            request_obj = {
                'method': flow['request'].get('method'),
                'url': flow['request'].get('url'),
                'headers': flow['request'].get('headers')
            }
            content_type = request_obj['headers'].get('Content-Type')
            if content_type and 'json' in content_type:
                data.request_data_type = 'json'
            elif content_type and 'html' in content_type:
                data.request_data_type = 'html'
            elif content_type and 'xml' in content_type:
                data.request_data_type = 'xml'
            elif content_type and 'text' in content_type:
                data.request_data_type = 'text'
            else:
                data.request_data_type = 'unknown'
            data.request_data.filetype = data.request_data_type
            data.request.content = json.dumps(request_obj, ensure_ascii=False, indent=4)
            if flow['request'].get('data'):
                data.request_data.content = flow['request'].get('data')
        if flow.get('response'):
            response_obj = {
                'code': flow['response'].get('code'),
                'headers': flow['response'].get('headers')
            }
            content_type = response_obj['headers'].get('Content-Type')
            if content_type and 'json' in content_type:
                data.response_data_type = 'json'
            elif content_type and 'html' in content_type:
                data.response_data_type = 'html'
            elif content_type and 'xml' in content_type:
                data.response_data_type = 'xml'
            elif content_type and 'text' in content_type:
                data.response_data_type = 'text'
            else:
                data.response_data_type = 'unknown'
            data.response_data.filetype = data.response_data_type
            data.response.content = json.dumps(response_obj, ensure_ascii=False, indent=4)
            if flow['response'].get('data'):
                data.response_data.content = flow['response'].get('data')
        return data


    def save(self):
        with codecs.open(self.path/self.info_filename, 'w', 'utf-8') as f:
            info = {
                'id': self.id,
                'name': self.name,
                'rule': self.rule,
                'request_data_type': self.request_data_type,
                'response_data_type': self.response_data_type
            }
            if self.flow and self.flow.get('request') and self.flow.get('request').get('url'):
                info['url'] = self.flow.get('request').get('url')
            json.dump(info, f, ensure_ascii=False, indent=4)
        
        self.request.save()
        self.request_data.save()
        self.response.save()
        self.response_data.save()
