import json
import codecs
from pathlib import Path
from bs4 import BeautifulSoup
from xml.dom import minidom


class DataFile:
    
    def __init__(self, data_obj, name, filetype='bin'):
        self.name = name
        self.path = Path(data_obj.path)/name
        self.filetype = filetype

    def load(self):
        _content = None
        if self.filetype in ['json', 'text', 'html', 'xml']:
            with codecs.open(self.path, 'r', 'utf-8') as f:
                _content = f.read()
        else:
            with codecs.open(self.path, 'rb', 'utf-8') as f:
                _content = f.read()
        return _content
    
    def save(self, val):
        if self.filetype in ['json', 'html', 'text', 'xml']:
            with codecs.open(self.path, 'w', 'utf-8') as f:
                f.write(val)

    @property
    def content(self):
        try:
            return self.load()
        except Exception:
            return None

    @content.setter
    def content(self, val):
        if not val:
            return

        _content = None
        if self.filetype == 'json':
            if type(val) == str:
                _content = json.dumps(json.loads(val), ensure_ascii=False, indent=4)
            else:
                _content = json.dumps(val, ensure_ascii=False, indent=4)
        elif self.filetype == 'html':
            _content = BeautifulSoup(val, features="html.parser").prettify()
        elif self.filetype == 'text':
            _content = val
        elif self.filetype == 'xml':
            _content = minidom.parseString(val).toprettyxml()

        if _content:
            self.save(_content)

    def json(self):
        return {
            'content': self.content,
            'filetype': self.filetype
        }