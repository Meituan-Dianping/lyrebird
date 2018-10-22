import json
import codecs
from pathlib import Path
from bs4 import BeautifulSoup
from xml.dom import minidom


class DataFile:
    
    def __init__(self, data_obj, name, filetype='json'):
        self.name = name
        self.path = Path(data_obj.path)/name
        self.filetype = filetype
        self._content = None

    def load(self):
        if self.filetype in ['json', 'text', 'html', 'xml']:
            with codecs.open(self.path, 'r', 'utf-8') as f:
                self._content = f.read()
    
    def save(self):
        if self._content and self.filetype in ['json', 'html', 'text', 'xml']:
            with codecs.open(self.path, 'w', 'utf-8') as f:
                f.write(self._content)

    @property
    def content(self):
        self.load()
        return self._content

    @content.setter
    def content(self, val):
        if self.filetype == 'json':
            self._content = json.dumps(json.loads(val), ensure_ascii=False, indent=4)
        elif self.filetype == 'html':
            self._content = BeautifulSoup(val, features="html.parser").prettify()
        elif self.filetype == 'text':
            self._content = val
        elif self.filetype == 'xml':
            self._content = minidom.parseString(val).toprettyxml()
        else:
            self._content = 'unknown data type'

