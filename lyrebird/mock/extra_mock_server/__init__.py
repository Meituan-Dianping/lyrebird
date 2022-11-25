from lyrebird.log import get_logger
from .server import serve, publish_init_status
from lyrebird.base_server import ProcessServer

logger = get_logger()


class ExtraMockServer(ProcessServer):
    def __init__(self) -> None:
        super().__init__()

        self._server_process = None

    def run(self, queue, config, *args, **kwargs):
        publish_init_status(queue, 'READY')
        serve(queue, config, *args, **kwargs)
