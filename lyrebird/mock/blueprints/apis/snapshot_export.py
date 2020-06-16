from flask import send_file
from flask_restful import Resource, request
from lyrebird.mock import context

class SnapshotExportFromEvent(Resource):
    def post(self):
        file = context.application.data_manager.export_snapshot_from_event(request.json)
        return send_file(file)

class SnapshotExportFromDM(Resource):
    def post(self):
        node_id = request.json.get("nodeId")
        file = context.application.data_manager.export_snapshot_from_dm(node_id)
        return send_file(file)
