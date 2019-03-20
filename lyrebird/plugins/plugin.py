

class Plugin:

    def __init__(self, project_name, entry_point_name=None, version=None, location=None, **kwargs):
        self.project_name = project_name
        self.entry_point_name = entry_point_name
        self.version = version
        self.location = location
        self.manifest = ManifestProxy(**kwargs)


class ManifestProxy:

    def __init__(self, **kwargs):
        self._manifest = kwargs
    
    def __getattr__(self, key):
        return self._manifest[key]
