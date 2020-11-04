from flask import render_template, Blueprint, send_file
import traceback
from lyrebird.mock import context
from lyrebird import log
from ... import version
# from .. import plugin_manager
from pathlib import Path


CLIENT_ROOT_DIR = Path(__file__).parent/'../../client/static'


ui = Blueprint('ui', __name__, url_prefix='/ui', static_folder=str(CLIENT_ROOT_DIR))


logger = log.get_logger()

@ui.route('/')
def index():
    return send_file(str(CLIENT_ROOT_DIR/'index.html'))
