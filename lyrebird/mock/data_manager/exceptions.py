class DataManagerError(Exception):
    pass


class DataRootDirNotExistsError(DataManagerError):
    pass


class DataGroupNotExistsError(DataManagerError):
    pass


class DataGroupInfoNotFoundError(DataManagerError):
    pass


class DataGroupIsNotDirError(DataManagerError):
    pass


class DataNotExistsError(DataManagerError):
    pass


class DataIsNotDirError(DataManagerError):
    pass


class DataInfoNotFoundError(DataManagerError):
    pass


class ActivateFailed(DataManagerError):
    pass

