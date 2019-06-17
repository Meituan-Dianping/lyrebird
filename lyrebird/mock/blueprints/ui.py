import os
from flask import render_template, Blueprint, send_file
import traceback
from lyrebird.mock import context
from lyrebird import log
from ... import version
from .. import plugin_manager
from bs4 import BeautifulSoup
import datetime
from pathlib import Path
from lyrebird import reporter


CLIENT_ROOT_DIR = Path(__file__).parent/'../../client/static'


ui = Blueprint('ui', __name__, url_prefix='/ui', static_folder=str(CLIENT_ROOT_DIR))


logger = log.get_logger()


def render_with_plugin(template_name_or_list, **context):
    web_plugins = []
    icon = ''
    for web_plugin_name in plugin_manager.web_plugins:
        try:
            obj = plugin_manager.web_plugins[web_plugin_name]
            if hasattr(obj, "index") and not obj.index():
                continue
            if hasattr(obj, "get_icon"):
                icon = obj.get_icon()
            if hasattr(obj, 'get_title'):
                title = obj.get_title()
            else:
                title = web_plugin_name.capitalize()
            web_plugins.append({'name': web_plugin_name, 'icon': icon, 'title': title})
        except Exception:
            logger.error(f'Load web plugin error. {traceback.format_exc()}')
    return render_template(template_name_or_list, web_plugins=web_plugins, version=version.VERSION, **context)


@ui.route('/')
def index():
    reporter.page_in('inspector')
    return send_file(str(CLIENT_ROOT_DIR/'index.html'))
