import os
import uuid
import time
import codecs
import tarfile
from lyrebird import log
from lyrebird.mock import dm
from lyrebird import application

logger = log.get_logger()

class Snapshot:
    @property
    def context_list(self):
        mock_data_repositories = application.config.raw().get("mock.data")
        
        snapshot_repositories = application.config.raw().get("snapshot")
        if not os.path.exists(snapshot_repositories):
            os.makedirs(snapshot_repositories)

        temp_dir_name = str(time.strftime(
            "%Y-%m-%d-%H-%M-%S", time.localtime()))+"-" + str(uuid.uuid4())
        os.makedirs(f"{snapshot_repositories}/{temp_dir_name}")
        return [
            mock_data_repositories,
            snapshot_repositories,
            temp_dir_name
            ]

    def write_prop_file(self,content,out_file_path):
        # write prop file
        prop_str = dm.PropWriter().parse(content)
        prop_file = f"{out_file_path}/.lyrebird_prop"
        with codecs.open(prop_file, "w") as f:
            f.write(prop_str)

    def compress_dir(self,compress_dir_path):
        t = tarfile.open(f"{compress_dir_path}.gz", "w:gz")
        for root, dir, files in os.walk(compress_dir_path):
            for file in files:
                fullpath = os.path.join(root, file)
                t.add(fullpath)
        t.close()
    
    def decompress_dir(self, input_path, output_path):
        tf = tarfile.open(input_path)
        tf.extractall(output_path)
        tf.close()
        logger.debug("decompress success")

    
                
        
snapshot = Snapshot()
