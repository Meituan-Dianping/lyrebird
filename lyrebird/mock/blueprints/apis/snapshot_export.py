from flask import send_file
from flask_restful import Resource, request
from lyrebird.mock.handlers.snapshot_handler import snapshot


class SnapshotExportFromEvent(Resource):
    def post(self):
        event_id = request.json.get("eventId")
        snapshot.snapshot_export_event(event_id)
        return send_file(snapshot.compress_dir_absolute_path)


class SnapshotExportFromDM(Resource):
    def post(self):
        node_id = request.json.get("nodeId")
        snapshot.snapshot_export_dm(node_id)
        return send_file(snapshot.compress_dir_absolute_path)
