import json
from pathlib import Path
from .exceptions import SerializeTargetNotExisit


class Serializable:

    def __init__(self, path):
        self.path = path
    
    def save(self):
        pass

    def load(self):
        pass


class SerializableDir(Serializable):

    pass


class SerializableJson(Serializable):

    pass


def from_path(target_path):
    target = Path(target_path)
    if target.is_dir():
        pass
    elif target.is_file():
        SerializableJson(target_path)
    else:
        SerializableDir(target_path)
    if not target.exists():
        raise SerializeTargetNotExisit(f'Target {target_path} not exisit')

