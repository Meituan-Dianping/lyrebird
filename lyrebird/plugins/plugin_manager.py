from lyrebird.base_server import StaticServer
from . import plugin_loader


class PluginManager(StaticServer):

    def __init__(self):
        self.plgin_path_list = []
        self.plgins = {}

    def reload(self, debug_plugin_path=None):
        self.plgins = plugin_loader.load(debug_plugin_path=debug_plugin_path)
