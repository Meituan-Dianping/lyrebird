from lyrebird.base_server import StaticServer
from . import plugin_loader


class PluginManager(StaticServer):

    def __init__(self):
        self.plugin_path_list = []
        self.plugins = {}

    def reload(self):
        self.plugins = {}
        self.plugins.update(plugin_loader.load_all_from_ep())
        for plugin_path in self.plugin_path_list:
            plugin = plugin_loader.load_from_path(plugin_path)
            self.plugins[plugin.project_name] = plugin
