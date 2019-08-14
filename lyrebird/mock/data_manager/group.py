import json
import codecs
import uuid
from pathlib import Path
import shutil
from .data import Data
from collections import OrderedDict
from .exceptions import DataGroupNotExistsError, DataGroupIsNotDirError, DataGroupInfoNotFoundError
from lyrebird.log import get_logger


logger = get_logger()


class Group:
    """
    DataGroup

    The info file (.lyrebird_prop) contains group info.
    {
        "id": "",
        "name": ""
    }

    """

    info_filename = '.lyrebird_prop'


    def __init__(self, gid, gname, gpath, gparent_id=None):
        self.id = gid
        self.name = gname
        self.parent_id = gparent_id
        self.path = gpath
        self.all_data = OrderedDict()

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
        _gparent = info.get('parent')

        group = cls(_gid, _gname, new_path, gparent_id=_gparent)
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
    
    def delete(self):
        """
        Delete group dir and subfile from disk
        """
        shutil.rmtree(self.path)

    def create_data(self, flow=None):
        data = Data.new_data(self.path, flow)
        self.all_data[data.id] = data
        return data
    
    def delete_data(self, data_id):
        data = self.all_data.pop(data_id)
        data.delete()

    def scan(self):
        for subfile in Path(self.path).iterdir():
            if not subfile.is_dir():
                continue
            try:
                data = Data.createify(subfile)
                if data:
                    self.all_data[data.id] = data
            except Exception as e:
                logger.error(f'Load data failed. {subfile}\n{e}')    

    def json(self, detail=False):
        json_obj = {
            'id': self.id,
            'name': self.name,
            'parent': self.parent_id,
        }
        if detail:
            json_obj['data_list'] = [self.all_data[data_id].json() for data_id in self.all_data]
        return json_obj
