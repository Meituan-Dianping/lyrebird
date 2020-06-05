from flask_restful import Resource, request
from flask import redirect
from lyrebird import application
from lyrebird.mock import context
from lyrebird import log
import requests
import tarfile
import json
import os
import shutil
from pathlib import Path
import uuid
import time
from ....version import VERSION


logger = log.get_logger()

importSnapshotUrl = None


class SanpshotImport(Resource):
    """
    SanpshotImport
    """

    def get(self, url):
        global importSnapshotUrl
        importSnapshotUrl = url
        return redirect(f'/ui/?v={VERSION}#/datamanager/import')

    def post(self):
        # get params
        global importSnapshotUrl
        logger.debug(importSnapshotUrl)
        parent_node = request.json.get('parentNode')
        if "id" not in parent_node:
            return application.make_fail_response(msg="has no param : parentNode.id")
        if importSnapshotUrl == None:
            return application.make_fail_response(msg="has no param : importSnapshotUrl")

        # get config
        conf = application.config.raw()
        logger.debug(f'conf:\n {conf}')
        mock_data_repositories = conf.get("mock.data")
        if not conf.get("snapshot"):
            return application.make_fail_response(msg=" config snapshot not defined")
        snapshot_import_repositories = conf.get("snapshot")
        logger.debug(f'snapshot_repositories: {snapshot_import_repositories}')
        if not os.path.exists(snapshot_import_repositories):
            os.makedirs(snapshot_import_repositories)
            logger.debug(f"make dir {snapshot_import_repositories} success")

        # initialization
        temp_file_name = str(time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()))+"-" + str(uuid.uuid4())
        compressed_file_path = f'{snapshot_import_repositories}/{temp_file_name}.gz'
        decompressed_file_path = f'{snapshot_import_repositories}/{temp_file_name}-unziped'
        logger.debug(f'temp file name: {temp_file_name}')

        # download
        resp = requests.get(importSnapshotUrl)
        with open(compressed_file_path, 'wb') as f:
            for chunck in resp.iter_content():
                f.write(chunck)
        logger.debug('download success')

        # decompress
        tf = tarfile.open(compressed_file_path)
        tf.extractall(decompressed_file_path)
        tf.close()
        logger.debug("decompress success")

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
