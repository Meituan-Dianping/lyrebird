from pathlib import Path
import json
from .group import Group
from .exceptions import DataRootDirNotExistsError, ActivateFailed
from .mock_router import MockRouter
from lyrebird.log import get_logger


logger = get_logger()


class DataManager:

    def __init__(self):
        self._root_path = None
        self.activated_group_id = None
        self.groups = {}
        self.router = MockRouter()

    @property
    def root(self):
        return self._root_path

    @root.setter
    def root(self, root_path):
        new_path = Path(root_path).expanduser()
        if not new_path.exists():
            new_path.mkdir(parents=True)
        self._root_path = new_path
        self.scan()

    def activate(self, group_id):
        if group_id in self.groups:
            self.activated_group_id = group_id
            group = self.groups.get(group_id)
            parent = self.groups.get(group.parent_id)
            self.router.switch_group(group, parent=parent)
        else:
            raise ActivateFailed(f'Group id not found {group_id}')

    def deactivate(self):
        self.activated_group_id = None
        self.router.switch_group(None)

    def create_group(self):
        group = Group.new_group(self.root)
        self.groups[group.id] = group
        return group

    def delete_group(self, group_id):
        group = self.groups.pop(group_id)
        if group:
            group.delete()

    def copy_croup(self):
        pass
    
    def scan(self):
        for sub_file in self.root.iterdir():
            if not sub_file.is_dir():
                continue
            try:
                group = Group.createify(sub_file)
                if group:
                    self.groups[group.id] = group
            except Exception as e:
                logger.error(f'Load group failed. {sub_file}\n{e}')    
    
