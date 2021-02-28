import imp
import traceback
from pathlib import Path
from lyrebird import application, log
from lyrebird.mock import context
PROP_FILE_NAME = '.lyrebird_prop'

logger = log.get_logger()

class DataController:
    def __init__(self):
        self.cache = {}
        self.cache_dir = Path('~/.lyrebird/mock_data/tmp').expanduser().absolute()

    @staticmethod
    def init_database(path):
        path = Path(path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        try:
            adapter = imp.load_source(path.stem, str(path))
            DataController.adapter_check(adapter)
            # context.application.data_manager.data_adapter = adapter
            context.application.data_manager.data_save_controller = adapter
            # context.application.data_manager._save_prop = adapter._save_prop
        except Exception:
            logger.error(f'Load mock data adapter {path} failed!\n{traceback.format_exc()}')

    @staticmethod
    def adapter_check(script):
        assert hasattr(script, '_save_prop'), "Adapter should have _save_prop attr"
        # assert callable(script._save_prop), "Adapter attr _save_prop should be callable"


class DataAdapter:
    def load_group(self):
        pass
