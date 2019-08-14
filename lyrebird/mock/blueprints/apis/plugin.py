from flask_restful import Resource
from lyrebird.mock.plugin_manager import plugins
from flask import jsonify
from lyrebird.mock import context


class Plugin(Resource):

    def get(self, plugin_name=None):
        plugins_dict = {}
        for name in plugins:
            plugins_dict[name] = dict(plugins[name])

        if not plugin_name:
            return jsonify(plugins_dict)

        _plugin = plugins.get(plugin_name)

        if not _plugin:
            return context.make_fail_response('Not found plugin')
        # /plugin/demo/static/
        return jsonify(plugins_dict[plugin_name])
