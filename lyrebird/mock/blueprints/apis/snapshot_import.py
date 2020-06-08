import os
import uuid
import time
import json
import shutil
import tarfile
import requests
from pathlib import Path
from lyrebird import log
from ....version import VERSION
from lyrebird import application
from lyrebird.mock import context
from flask import redirect
from flask_restful import Resource, request
from lyrebird.mock.handlers.snapshot_handler import snapshot


logger = log.get_logger()
importSnapshotUrl = None

class SanpshotImport(Resource):
    """
    SanpshotImport
    """

    def get(self, url):
        global importSnapshotUrl
        importSnapshotUrl = url
        return redirect(f"/ui/?v={VERSION}#/datamanager/import")

    def post(self):
        # get params
        global importSnapshotUrl
        logger.debug(f"importSnapshotUrl: {importSnapshotUrl}")
        parent_node = request.json.get("parentNode")
        if "id" not in parent_node:
            return application.make_fail_response(msg="object has no attribute : parentNode.id")
        if importSnapshotUrl == None:
            return application.make_fail_response(msg="object has no attribute : importSnapshotUrl")

        # get config
        mock_data_repositories, snapshot_repositories, temp_dir_name = snapshot.context_list
        temp_dir_absolute_path = f"{snapshot_repositories}/{temp_dir_name}"
        compressed_file_path = f"{temp_dir_absolute_path}.gz"
        decompressed_file_path = f"{temp_dir_absolute_path}-unziped"

        # download
        resp = requests.get(importSnapshotUrl)
        with open(compressed_file_path, "wb") as f:
            for chunck in resp.iter_content():
                f.write(chunck)

        # decompress
        snapshot.decompress_dir(compressed_file_path,decompressed_file_path)

        # load lyrebird_prop
        decompressed_innermost_path_list = []
        def find_prop(path):
            file_list = os.listdir(path)
            for file in file_list:
                filepath = os.path.join(path, file)
                if ".lyrebird_prop" in filepath:
                    decompressed_innermost_path_list.append(filepath)
                if os.path.isdir(filepath):
                    find_prop(filepath)
        find_prop(path=decompressed_file_path)
        logger.debug(decompressed_innermost_path_list)
        if len(decompressed_innermost_path_list) != 1:
            return application.make_fail_response(msg="multiple prop files exist in snapshot directory")
        prop_file_path = decompressed_innermost_path_list[0]
        mock_data_innermost_path = str(decompressed_innermost_path_list[0]).split("/.lyrebird_prop")[0]
        mockdata_node = json.loads(Path(prop_file_path).read_text())
        
        # save data
        if context.application.data_manager.id_map.get(mockdata_node["id"]):
            return application.make_fail_response("snapshot is already exists")
        
        # import snapshot
        context.application.data_manager.import_snapshot(
            parent_id=parent_node["id"],
            snapshot_prop_obj=mockdata_node
        )
        
        for file in os.listdir(mock_data_innermost_path):
            if "." not in file:
                file_path = os.path.join(mock_data_innermost_path, file)
                logger.debug(file_path)
                shutil.copy(
                    file_path,
                    mock_data_repositories
                )
        context.application.data_manager.activate(_id=mockdata_node["id"])
        return application.make_ok_response()
