from lyrebird.mock.plugin_manager import PluginView


class PluginForTest(PluginView):

    def api_func1(self):
        pass

    def on_create(self):
        self.add_url_rule('/test', view_func=self.api_func1)

def test_oncreate():
    plugin = PluginForTest()
    plugin.on_create()
    assert len(plugin.rules) == 1
    rule = plugin.rules[0]
    assert rule.rule == '/test'
    assert rule.view_func == plugin.api_func1
    