from pathlib import Path
import json
import codecs


def dict_to_obj(d, o):
    return o.__dict__.update(d)

def obj_to_dict(o, d):
    pass


class Request:
    
    def __init__(self):
        self.url = None        
        self.version = None
        self.method = None
        self.scheme = None
        self.host = None
        self.path = None
        self.qurey = None
        self.headers = {}
        self.data = None
        self._path: Path = None

    def save(self):
        pass

    def load(self):
        req = self._path/'request.json'
        if req.exists:
            with codecs.open(str(req)) as f:
                req_json_obj = json.loads(f.read())
                dict_to_obj(req_json_obj, self)
        req_data_json = self._path/'request_data.json'
        req_data_txt = self._path/'request_data.bin'
        if req_data_json.exists():
            with codecs.open(str(req_data_json)) as f:
                req_data_obj = json.loads(f.read())
                self.data = {}
                dict_to_obj(req_data_obj, self.data)
        elif req_data_txt.exists():
            with codecs.open(str(req_data_txt)) as f:
                req_data_obj = json.loads(f.read())
                self.data = {}
                dict_to_obj(req_data_obj, self.data)

        


class Response:
    
    def __init__(self):
        self.status = -1
        self.headers = {}
        self.data = None

    def save(self):
        pass

    def load(self):
        pass


class Flow:
    
    def __init__(self):
        self.id = None
        self.path: Path = None
        self.request: Request = None
        self.response: Response = None
        self.timings = None

    @classmethod
    def from_path(cls, path):
        instance = cls()
        instance.path = path
        instance.load()
        return instance

    def save(self):
        pass
    
    def load(self):
        self.request = Request()
        self.request._path = self.path
        self.request.load()
