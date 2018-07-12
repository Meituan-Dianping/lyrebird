from .data import Flow
from pathlib import Path
import codecs
import json
from .exceptions import GroupNotFoundError



class Group:
    
    def __init__(self, path: Path):
        self.path = path
        self.name = self.path.name
        self.data_array = []
        self.request_map = {}
    
    def save(self):
        # create group dir
        if not self.path.exists():
            self.path.mkdir()
        # update map file

        # update data
        for data in self.data_array:
            data.save()
    
    def load(self):
        if not self.path.exists():
            raise GroupNotFoundError(f'Load group failed. Group {self.path} not found.')
        for sub_file in self.path.iterdir():
            if sub_file.is_file() and sub_file.name == 'conf.json':
                with codecs.open(str(sub_file) , 'r', 'utf-8') as f:
                    self.request_map = json.loads(f.read())
            elif sub_file.is_dir():
                data = Flow.from_path(sub_file)
                self.data_array.append(data)

    def add_data(self, data):
        pass

    def delete_data(self, data):
        pass

    def find_data(self, url, **kwargs):
        pass
