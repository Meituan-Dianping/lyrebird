import os
import uuid
import time
import codecs
import tarfile
import requests
from lyrebird import log
from lyrebird import application
from lyrebird.mock import context
from urllib.parse import urlparse
logger = log.get_logger()


class Snapshot():
    def __init__(self):
        self.snapshot_import_uri = None
        self.snapshot_repositories = None
        self.temp_dir_name = None
        self.compress_dir_absolute_path = None
        self.decompress_dir_absolute_path = None
        self.temp_dir_absolute_path = None

    def snapshot_import(self, pid):
        self._init_data()
        self._save_compressed_tar_file()
        self._decompress_snapshot(self.compress_dir_absolute_path, self.decompress_dir_absolute_path)
        context.application.data_manager.import_snapshot(pid, self.decompress_dir_absolute_path)

    def snapshot_export_event(self, event_id):
        self._init_data()
        event_detail = self._get_event_detail(event_id)

        prop_file_content = event_detail.get("snapshot")
        data_list = event_detail.get("events")
        data_list_id_map = {}
        for data in data_list:
            data_list_id_map.update({data.get("id"): data})

        print(data_list_id_map)
        context.application.data_manager.export_snapshot(
            prop_file_content,
            self.snapshot_repositories,
            self.temp_dir_name,
            context.application.data_manager._cp_data_from_event_callback,
            event_list_id_map=data_list_id_map
        )
        self._compress_dir(self.temp_dir_absolute_path)
        print("success")

    def snapshot_export_dm(self, node_id):
        self._init_data()
        context.application.data_manager.node_check(node_id)
        node = context.application.data_manager.id_map.get(node_id)
        context.application.data_manager.export_snapshot(
            node,
            self.snapshot_repositories,
            self.temp_dir_name,
            context.application.data_manager._cp_data_from_file_callback
        )
        self._compress_dir(self.temp_dir_absolute_path)
        print("success")

    def _init_data(self):
        self.snapshot_repositories = f"{application._cm.ROOT}/snapshot"
        self._check_snapshot_repositories_exist()
        self._make_snapshot_temp_dir()
        self.compress_dir_absolute_path = f"{self.snapshot_repositories}/{self.temp_dir_name}.tar.gz"
        self.decompress_dir_absolute_path = f"{self.snapshot_repositories}/{self.temp_dir_name}-unziped"

    def _check_snapshot_repositories_exist(self):
        if not os.path.exists(self.snapshot_repositories):
            os.mkdir(self.snapshot_repositories)

    def _make_snapshot_temp_dir(self):
        self.temp_dir_name = f"{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}-{str(uuid.uuid4())}"
        os.mkdir(f"{self.snapshot_repositories}/{self.temp_dir_name}")
        self.temp_dir_absolute_path = f"{self.snapshot_repositories}/{self.temp_dir_name}"

    def _save_compressed_tar_file(self):
        if not self.snapshot_import_uri:
            raise SnapshotImportUriNotFound
        snapshot_import_uri_parsed = urlparse(self.snapshot_import_uri)
        if "http" in snapshot_import_uri_parsed.scheme:
            resp = requests.get(self.snapshot_import_uri)
            with open(self.compress_dir_absolute_path, "wb") as f:
                for chunck in resp.iter_content():
                    f.write(chunck)
        elif "file" in snapshot_import_uri_parsed.scheme:
            with codecs.open(snapshot_import_uri_parsed.path, "rb") as inputfile, codecs.open(self.compress_dir_absolute_path, "wb") as outputfile:
                read_content = inputfile.read()
                outputfile.write(read_content)
            print(self.compress_dir_absolute_path)
        else:
            raise SnapshotImportUriSchemeIllegal

    def _decompress_snapshot(self, compress_dir, decompress_dir):
        tf = tarfile.open(compress_dir)
        tf.extractall(decompress_dir)
        tf.close()
        logger.debug("decompress success")

    def _compress_dir(self, temp_dir_absolute_path):
        tar = tarfile.open(f"{temp_dir_absolute_path}.tar.gz", "w:gz")
        for root, dirs, files in os.walk(temp_dir_absolute_path):
            for file in files:
                logger.debug(root, dirs, files)
                fullpath = os.path.join(root, file)
                tar.add(fullpath)
        tar.close()

    def _get_event_detail(self, event_id):
        db = application.server["db"]
        event_detail = db.get_event_detail_by_event_id(event_id)
        return event_detail


snapshot = Snapshot()


# -----------------
# Exceptions
# -----------------

class SnapshotImportUriNotFound(Exception):
    pass


class SnapshotImportUriSchemeIllegal(Exception):
    pass

