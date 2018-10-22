import json
import codecs
import uuid
from pathlib import Path
from .data import Data
from .exceptions import DataGroupNotExistsError, DataGroupIsNotDirError, DataGroupInfoNotFoundError


class Group:
    """
    DataGroup

    Keep all flow data.

    The .info file contains group info.
    {
        "id": "",
        "name": ""
    }

    """

    info_filename = '.info'


    def __init__(self, gid, gname, gpath, gparent_id=None):
        self.id = gid
        self.name = gname
        self.parent_id = gparent_id
        self.path = gpath
        self.data_list = []

    @classmethod
    def createify(cls, group_path):
        """
        Create group object if group_path exists
        """
        new_path = Path(group_path)
        if not new_path.exists():
            raise DataGroupNotExistsError(group_path)
        if not new_path.is_dir():
            raise DataGroupIsNotDirError(group_path)
        # Read group info
        with codecs.open(new_path/cls.info_filename, 'r' , 'utf-8') as f:
            info = json.load(f)
        if not info:
            raise DataGroupInfoNotFoundError(new_path)

        _gid = info.get('id')
        _gname = info.get('name')

        group = cls(_gid, _gname, new_path)
        group.scan()
        return group

    @classmethod
    def new_group(cls, group_dir):
        """
        Make a new group
        """
        _id = str(uuid.uuid4())
        group = cls(_id, _id, Path(group_dir)/_id)
        Path(group.path).mkdir(parents=True, exist_ok=True)
        return group

    def save(self):
        with codecs.open(self.path/self.info_filename, 'w', 'utf-8') as f:
            info = {
                'id': self.id,
                'name': self.name,
                'parent': self.parent_id
            }
            json.dump(info, f, ensure_ascii=False, indent=4)

    def create_data(self, flow=None):
        data = Data.new_data(self.path, flow)
        self.data_list.append(data)
        return data

    def scan(self):
        for subfile in Path(self.path).iterdir():
            data_dir = Path(self.path)/subfile
            if not data_dir.is_dir():
                continue
            data = Data.createify(data_dir)
            if data:
                self.data_list.append(data)
