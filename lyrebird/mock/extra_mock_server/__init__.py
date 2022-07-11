
import multiprocessing

from lyrebird import application
from lyrebird.log import get_logger
from .server import serve


logger = get_logger()


class ExtraMockServer():
    def __init__(self) -> None:
        self._server_process = None

    def start(self):
        self._server_process = multiprocessing.Process(
            group=None,
            daemon=True,
            target=serve,
            kwargs={'config': application.config.raw()})
        self._server_process.start()

    def stop(self):
        if self._server_process:
            self._server_process.terminate()
            logger.warning(f'MockServer shutdown')
            self._server_process = None
