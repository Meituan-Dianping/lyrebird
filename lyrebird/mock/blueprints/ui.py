import os
from flask import render_template, Blueprint
import traceback
from lyrebird.mock import context
from lyrebird import log
from ... import version
from .. import plugin_manager
from bs4 import BeautifulSoup
import datetime
from ..reporter import report_handler


ui = Blueprint('ui', __name__, url_prefix='/ui', template_folder='../templates', static_folder='../static')

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
    report_handler.page_in('inspector')
    return render_with_plugin('inspector.html')


@ui.route('/data_manager')
def data_manager():
    report_handler.page_in('data_manager')
    return render_with_plugin('data_manager_v2.html')


@ui.route('/plugin/base/<string:name>')
def plugin_base(name):
    report_handler.page_in(name)
    plugin = plugin_manager.web_plugins.get(name)
    if not plugin:
        return "Plugin not found"
    
    web_content = plugin.index()
    soup = BeautifulSoup(web_content, 'html.parser')

    # set all javascripts into script block
    all_scripts = []
    for javascript_tag in soup.find_all('script'):
        all_scripts.append(javascript_tag)
        javascript_tag.extract()
    # set all css link into header
    all_css = []
    for css_tag in soup.find_all('link'):
        all_css.append(css_tag)
        css_tag.extract()
    return render_with_plugin('plugin.html', current_plugin={'name': name},
                              plugin_content=str(soup),
                              plugin_javascript=all_scripts,
                              plugin_css=all_css)


@ui.route('/settings')
def settings():
    report_handler.page_in('settings')
    return render_with_plugin('settings.html')
