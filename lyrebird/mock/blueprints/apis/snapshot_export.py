from flask import send_file
from flask_restful import Resource, request
from lyrebird.mock import context

class SnapshotExport(Resource):
    def get(self, group_id):
        file = context.application.data_manager.export_snapshot_from_dm(group_id)
        return send_file(file)

    def post(self):
        file = context.application.data_manager.export_snapshot_from_event(request.json)
        return send_file(file)
