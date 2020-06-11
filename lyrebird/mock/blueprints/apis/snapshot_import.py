from flask import redirect
from ....version import VERSION
from lyrebird import application
from flask_restful import Resource, request
from lyrebird.mock.handlers.snapshot_handler import snapshot


class SanpshotImport(Resource):
    def get(self, url):
        snapshot.snapshot_import_uri = url
        return redirect(f"/ui/?v={VERSION}#/datamanager/import")

    def post(self):
        parent_node = request.json.get("parentNode")
        if "id" not in parent_node:
            return application.make_fail_response(msg="object has no attribute : parentNode.id")
        snapshot.snapshot_import(parent_node["id"])
        return application.make_ok_response()

