from lyrebird.log import get_logger
from .server import serve, publish_init_status
from lyrebird.base_server import ProcessServer

logger = get_logger()


class ExtraMockServer(ProcessServer):

    def run(self, async_obj, config, *args, **kwargs):
        log_queue = async_obj['logger_queue']
        msg_queue = async_obj['msg_queue']
        publish_init_status(msg_queue, 'READY')
        serve(msg_queue, config, log_queue, *args, **kwargs)
