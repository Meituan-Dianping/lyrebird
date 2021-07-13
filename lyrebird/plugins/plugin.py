

class Plugin:

    def __init__(self, project_name, entry_point_name=None, version=None, location=None, **kwargs):
        self.project_name = project_name
        self.entry_point_name = entry_point_name
        self.version = version
        self.location = location
        self.manifest = ManifestProxy(**kwargs)
        self.status = []

    @staticmethod
    def default():
        return dict(
            view=('dist', 'index.html'),
            icon='mdi-widgets',
            api=[],
            background=[],
            event=[],
            on_request=[],
            on_response=[],
            on_request_upstream=[],
            on_response_upstream=[],
            status=[]
        )


class ManifestProxy:

    def __init__(self, **kwargs):
        self._manifest = kwargs
        self._set_default()

    def __getattr__(self, key):
        return self._manifest[key]

    def _set_default(self):
        default = Plugin.default()
        for default_key in default:
            if default_key in self._manifest:
                continue
            else:
                self._manifest[default_key] = default[default_key]
