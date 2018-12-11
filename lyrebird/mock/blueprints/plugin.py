from flask import render_template, Blueprint
from bs4 import BeautifulSoup
from ..reporter import report_handler
from .. import plugin_manager


plugin = Blueprint('plugin', __name__, url_prefix='/plugin', template_folder='../templates', static_folder='../static')


@plugin.route('/<string:name>')
def plugin_base(name):
    report_handler.page_in(name)
    plugin = plugin_manager.plugins.get(name)
    if not plugin:
        return "Plugin not found"
    ui = plugin['beta_web']
    web_content = ui.index()
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
    return render_template('plugin.html', 
                            plugin_content=str(soup),
                            plugin_javascript=all_scripts,
                            plugin_css=all_css)

