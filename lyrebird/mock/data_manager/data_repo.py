from .data_group import Group
from .exceptions import GroupNotFoundError, GroupAlreadyExisit
from pathlib import Path


class Repo:
    """
    Mock数据仓库
    """
    def __init__(self, repo_path):
        self.path = Path(repo_path)
        self.groups = {}
        self.activated_group = None

    def activate(self, name):
        group = self.groups.get(name)
        if not group:
            raise GroupNotFoundError(f'Group {name} not found')
        self.activated_group = group

    def deactivate(self, name):
        if self.activated_group and self.activated_group.name == name:
            self.activated_group = None

    def reset(self):
        self.activated_group = None

    def create_group(self, name):
        if self.groups.get(name):
            raise GroupAlreadyExisit(f'Group {name} already exisit')
        self.groups[name] = Group(name)
        self.groups[name].save()

    def delete_group(self, name):
        group = self.groups.pop(name)
        if not group:
            raise GroupNotFoundError(f'Group {name} not found')
        group.remove()

    def load(self):
        for sub_file in self.path.iterdir():
            if not sub_file.is_dir():
                continue
            group = Group(sub_file)
            group.load()
            self.groups[group.name] = group 

    def save(self):
        pass
