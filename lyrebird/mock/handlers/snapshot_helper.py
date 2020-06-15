import os
import uuid
import time
import codecs
import tarfile
import requests
from lyrebird import log
from lyrebird import application
from urllib.parse import urlparse
logger = log.get_logger()



class SnapshotHelper():

    def get_snapshot_path(self):
        snapshot_repositories = f"{application._cm.ROOT}/snapshot"
        if not os.path.exists(snapshot_repositories):
            os.mkdir(snapshot_repositories)
        temp_dir_name = f"{time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())}-{str(uuid.uuid4())}"
        os.mkdir(f"{snapshot_repositories}/{temp_dir_name}")
        snapshot_path = f"{snapshot_repositories}/{temp_dir_name}"
        return snapshot_path

    def save_compressed_file(self, snapshot_path):
        from lyrebird.mock.blueprints.apis.snapshot_import import snapshot_import_uri
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
        cur_path = os.getcwd()
        full_path_in = os.path.join(cur_path, dir_in)
        os.chdir(full_path_in)
        tar = tarfile.open(f"{output_path}.lb", "w:gz")
        for root, dir, files in os.walk(full_path_in):
            for file in files:
                fullpath = file
                tar.add(fullpath, recursive=False)
        tar.close()
        os.chdir(cur_path)
        logger.debug(f"compress snapshot : ['{output_path}.lb'] success")

    def get_data_id_map(self, node, data_id_map):
        if 'id' in node and node["type"] == "data":
            data_id_map[node['id']] = node
        if 'children' in node:
            for child in node['children']:
                self.get_data_id_map(child, data_id_map)


# -----------------
# Exceptions
# -----------------

class SnapshotImportUriNotFound(Exception):
    pass


class SnapshotImportUriSchemeIllegal(Exception):
    pass
