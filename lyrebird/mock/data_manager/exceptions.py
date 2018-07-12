class DataManagerError(Exception):
    pass


class GroupNotFoundError(DataManagerError):
    pass


class GroupAlreadyExisit(DataManagerError):
    pass


class SerializeTargetNotExisit(DataManagerError):
    pass
