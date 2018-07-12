from lyrebird.mock.plugin_manager import PluginView


class TestPlugin(PluginView):

    def api_func1(self):
        pass

    def on_create(self):
        self.add_url_rule('/', view_func=self.api_func1)

def test_oncreate():
    plugin = TestPlugin()
    plugin.on_create()
    assert len(plugin.rules) == 1
    rule = plugin.rules[0]
    assert rule.rule == '/'
    assert rule.view_func == plugin.api_func1
    