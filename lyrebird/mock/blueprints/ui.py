from flask import Blueprint, send_file
from lyrebird import log
from pathlib import Path
import sys
import os


CURRENT_DIR = os.path.dirname(__file__)

CLIENT_ROOT_DIR = Path(CURRENT_DIR).parent.parent/'client/static'


ui = Blueprint('ui', __name__, url_prefix='/ui', static_folder=str(CLIENT_ROOT_DIR))


logger = log.get_logger()

logger.debug(f'[UI] cwd: {os.getcwd()}')
logger.debug(f'[sys.excutable] : {sys.executable}')
logger.debug(f'[static-dir] : {CLIENT_ROOT_DIR}')


@ui.route('/')
def index():
    return send_file(str(CLIENT_ROOT_DIR/'index.html'))
