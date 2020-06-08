import os
import uuid
import time
import json
import codecs
import tarfile
from lyrebird import log
from flask import Response
from lyrebird.mock import dm
from lyrebird import application
from lyrebird.mock import context
from flask_restful import Resource, request
from lyrebird.mock.handlers.snapshot_handler import snapshot


logger = log.get_logger()


class SnapshotExportFromDM(Resource):
    def post(self):
        node_id = request.json.get("nodeId")
        mock_data_repositories, snapshot_repositories, temp_dir_name = snapshot.context_list

        # copy file from dm
        context.application.data_manager.export_snapshot(
            node_id=node_id,
            export_root_path=snapshot_repositories,
            export_dir_name=temp_dir_name,
            mock_data_repositories=mock_data_repositories
        )

        # compress export dir
        snapshot.compress_dir(f"{snapshot_repositories}/{temp_dir_name}")

        # stream return
        def generate():
            with open(f"{snapshot_repositories}/{temp_dir_name}.gz", "rb") as f:
                while True:
                    data = f.read(2048)
                    if not data:
                        break
                    yield data
        return Response(generate())


class SnapshotExportFromEvent(Resource):
    def get(self):
        # event_id = request.json.get("event_id")
        event_id = "c6c14109-d649-4bde-84be-ef342b658263"
        db = application.server["db"]
        event_detail = db.get_event_detail_by_event_id(event_id)

        prop_file_content = event_detail.get("flow").get("snapshot")
        data_list = event_detail.get("flow").get("events")
        data_list_id_map = {}
        for data in data_list:
            data_list_id_map.update({data.get("id"):data})

        mock_data_repositories, snapshot_repositories, temp_dir_name = snapshot.context_list
        
        # create prop file and data file
        def _modify_and_cp_file(node):
            if "children" not in node:
                return
            for child in node["children"]:
                old_child_id = child["id"]
                child["id"] = str(uuid.uuid4())
                child["parent_id"] = node["id"]
                if child["type"] == "group":
                    _modify_and_cp_file(child)
                if child["type"] == "data":
                    with codecs.open(f"{snapshot_repositories}/{temp_dir_name}/{child['id']}", "w") as outputfile:
                        content = data_list_id_map.get(old_child_id)
                        content["id"] = child["id"]
                        new_id_data = json.dumps(content, ensure_ascii=False)
                        outputfile.write(new_id_data)
        _modify_and_cp_file(prop_file_content)

        # write prop file
        snapshot.write_prop_file(prop_file_content, f"{snapshot_repositories}/{temp_dir_name}")

        # compress export dir
        snapshot.compress_dir(f"{snapshot_repositories}/{temp_dir_name}")
        
        # stream return
        def generate():
            with open(f"{snapshot_repositories}/{temp_dir_name}.gz", "rb") as f:
                while True:
                    data = f.read(2048)
                    if not data:
                        break
                    yield data
        return Response(generate())
