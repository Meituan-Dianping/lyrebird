import os
import uuid
import time
import codecs
import tarfile
import requests
from lyrebird import log
from lyrebird import application
from urllib.parse import urlparse
from pathlib import Path
logger = log.get_logger()


class SnapshotHelper():

    def get_snapshot_path(self):
        snapshot_repositories = application._cm.ROOT / "snapshot"
        if not snapshot_repositories.exists():
            snapshot_repositories.mkdir()
        temp_dir_name = f"{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}-{str(uuid.uuid4())}"
        snapshot_path = snapshot_repositories / temp_dir_name
        snapshot_path.mkdir()
        return snapshot_path

    def save_compressed_file(self, snapshot_path):
        snapshot_import_uri = application.snapshot_import_uri
        if not snapshot_import_uri:
            raise SnapshotImportUriNotFound
        parsed_uri = urlparse(snapshot_import_uri)
        if "http" in parsed_uri.scheme:
            resp = requests.get(snapshot_import_uri)
            with open(f"{snapshot_path}.lb", "wb") as f:
                for chunck in resp.iter_content():
                    f.write(chunck)
        elif "file" in parsed_uri.scheme:
            with codecs.open(parsed_uri.path, "rb") as inputfile, codecs.open(f"{snapshot_path}.lb", "wb") as outputfile:
                read_content = inputfile.read()
                outputfile.write(read_content)
        else:
            raise SnapshotImportUriSchemeIllegal

    def decompress_snapshot(self, compress_dir, decompress_dir):
        tf = tarfile.open(compress_dir)
        tf.extractall(decompress_dir)
        tf.close()
        logger.debug(f"decompress [{compress_dir}] to [{decompress_dir}] success")

    def compress_snapshot(self, output_path, dir_in):
        cur_path = Path.cwd()
        full_path_in = cur_path.joinpath(dir_in)
        os.chdir(full_path_in)
        tar = tarfile.open(f"{output_path}.lb", "w:gz")
        for root, dirs, files in os.walk(full_path_in):
            logger.debug(f"compress use root: {root}, dirs: {dirs}, files: {files}")
            for file in files:
                tar.add(file, recursive=False)
        tar.close()
        os.chdir(cur_path)
        logger.debug(f"compress snapshot : ['{output_path}.lb'] success")

    def get_data_id_map(self, node, data_id_map):
        if 'id' in node and node['type'] == 'data':
            data_id_map[node['id']] = node
        if 'children' in node and node['type'] == 'group':
            for child in node['children']:
                self.get_data_id_map(child, data_id_map)


# -----------------
# Exceptions
# -----------------
class SnapshotImportUriNotFound(Exception):
    pass


class SnapshotImportUriSchemeIllegal(Exception):
    pass
