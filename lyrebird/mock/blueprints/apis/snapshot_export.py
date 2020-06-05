from flask_restful import Resource, request
from flask import Response
from lyrebird import application
from lyrebird.mock import context
from lyrebird import log
import tarfile
import json
import os
import uuid
import time

logger = log.get_logger()


class SnapshotExport(Resource):
    def post(self):
        if not request.json.get("nodeId"):
            return application.make_fail_response(f"获取导出nodeId失败")
        node_id = request.json.get("nodeId")

        # get config
        conf = application.config.raw()
        logger.debug(f'conf:\n {conf}')
        mock_data_repositories = conf.get("mock.data")
        if not conf.get("snapshot"):
            return application.make_fail_response(msg=" config snapshot not defined")
        snapshot_export_repositories = conf.get("snapshot")
        logger.debug(f'snapshot_repositories: {snapshot_export_repositories}')
        if not os.path.exists(snapshot_export_repositories):
            os.makedirs(snapshot_export_repositories)
            logger.debug(f"make dir {snapshot_export_repositories} success")

        # defind output dir
        export_dir_name = str(time.strftime(
            "%Y-%m-%d-%H-%M-%S", time.localtime()))+"-" + str(uuid.uuid4())

        # export dm
        context.application.data_manager.export_snapshot(
            node_id=node_id,
            export_root_path=snapshot_export_repositories,
            export_dir_name=export_dir_name,
            mock_data_repositories=mock_data_repositories
        )

        # tar export dir
        t = tarfile.open(f'{snapshot_export_repositories}/{export_dir_name}.gz', "w:gz")
        for root, dir, files in os.walk(f'{snapshot_export_repositories}/{export_dir_name}'):
            for file in files:
                fullpath = os.path.join(root, file)
                t.add(fullpath)
        t.close()

        # stream return
        def generate():
            with open(f'{snapshot_export_repositories}/{export_dir_name}.gz', "rb") as f:
                while True:
                    data = f.read(2048)  # 每次读取指定的长度
                    import time
                    time.sleep(1)
                    if not data:
                        break
                    yield data
        return Response(generate())
