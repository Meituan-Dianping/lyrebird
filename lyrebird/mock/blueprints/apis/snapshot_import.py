from flask import redirect
from ....version import VERSION
from lyrebird import application
from flask_restful import Resource, request
from lyrebird.mock import context


class SanpshotImport(Resource):
    def get(self, url):
        application.snapshot_import_uri = url
        application.active_menu = {
            'name': 'datamanager',
            'title': 'DataManager',
            'type': 'router',
            'path': '/datamanager'
        }
        return redirect(f"/ui/?v={VERSION}#/datamanager/import")

    def post(self):
        parent_node = request.json.get("parentNode")
        snapshot_name = request.json.get('snapshotName', '')
        if "id" not in parent_node:
            return application.make_fail_response(msg="object has no attribute : parentNode.id")
        context.application.data_manager.import_snapshot(parent_node["id"], snapshot_name)
        return application.make_ok_response()


class SnapShotImportDetail(Resource):
    def get(self):
        snapshot_detail = context.application.data_manager.decompress_snapshot()['snapshot_detail']
        snapshot_detail.pop('children')
        return application.make_ok_response(data=snapshot_detail)
