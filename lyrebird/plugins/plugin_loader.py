import os
import imp
import inspect
import traceback
from pathlib import Path
from collections import namedtuple

import pkg_resources
import setuptools

from ..log import get_logger
from .plugin import Plugin

from lyrebird import application
import sys

logger = get_logger()


PLUGIN_ENTRY_POINT = "lyrebird_plugin"
manifest_cache = []


class ManifestError(Exception):
    pass


def manifest(**options):
    """
    Plugin entry method

        Usage:

        manifest(
            # Set UI entry point.
            # Each page need a tuple : (path, static-file-dir, html-file-name)
            # path - base url for plugin main page， userally it is '/'
            # static-file-dir - your frontent output dir
            # html-file-name (optional)  - default=index.html

            view=('/', 'static'),

            # Set plugin API.
            # Each API option is a tuple : (path, api-function, methods)
            # path - API path. If path='/status', the url will be 'http://lyrebid-host:port/plugin/plugin-name/api/status
            # api-function - API callback function. You can use flask.request for getting request info in this function.
            # methods - Same as flask methods.

            api=[
                ('status', plugin.mycallback, ['GET', 'POST'])
            ],

            # Set background task into a lyrebird task thread.

            background=[
                (task_name, task_function)
            ],

            # Set event listener
            # Each listener is a tuple : (channel, callback_function)
            # channel - Register listener to this channel
            # callback_function - This function will receive new event from the channel registered

            event=[
                ('flow', plugin.event_handler)
            ],

            # Set status bar text

            status=[
                plugin.StatusItem
            ]
        )
    """
    caller_info = inspect.stack()[1]
    manifest_cache.append((options, caller_info))


def is_plugin_enable(manifest_id):
    plugin_list = application.config.get('extension.plugin.enable')
    if plugin_list is None:
        return True
    return manifest_id in plugin_list


def load_all_from_ep():
    plugins = {}
    # Load plugin from installed packages by entry point 'lyrebird_plugin'
    for ep in pkg_resources.iter_entry_points(PLUGIN_ENTRY_POINT):
        try:
            plugin = load_plugin_from_ep(ep)
            if not is_plugin_enable(plugin.project_name):
                logger.info(f'Load plugin info: {plugin.project_name} is not enable.')
                continue

            if plugin.project_name in plugins:
                logger.error('Load plugin failed: More than one manifest in this plugin')
                continue
        except Exception as e:
            logger.error(f'Load plugin {ep.name} failed: {ep.dist}\n{e}\n{traceback.format_exc()}')
            continue
        plugins[plugin.project_name] = plugin
        logger.info(f'Load plugin from ep success: {plugin.project_name}')
    return plugins


def load_plugin_from_ep(ep):
    global manifest_cache
    manifest_cache = []

    ep_instance = ep.load()

    # There can only be one manifest in each plugin
    if len(manifest_cache) > 1:
        raise ManifestError('More than one manifest in this plugin')
    if len(manifest_cache) == 0:
        raise ManifestError('Not found manifest in plugin')

    # TODO
    manifest = manifest_cache[0][0]
    plugin = Plugin(
        manifest['id'],
        entry_point_name=ep.name,
        version=ep.dist.version,
        location=str(Path(ep_instance.__file__).parent),
        **manifest)

    return plugin


def load_from_path(plugin_path):
    global manifest_cache
    manifest_cache = []

    packages = setuptools.find_packages(plugin_path)
    for pkg in packages:
        manifest_file = Path(plugin_path)/pkg/'manifest.py'
        if not manifest_file.exists():
            continue
        if pkg in sys.modules:
            sys.modules.pop(pkg)
        if pkg+'.manifest' in sys.modules:
            sys.modules.pop(pkg+'.manifest')
        imp.load_package(pkg, Path(plugin_path)/pkg)
        __import__(pkg+'.manifest')

    # There can only one manifest in each plugin
    if len(manifest_cache) > 1:
        raise ManifestError('More than one manifest in this plugin')
    if len(manifest_cache) == 0:
        raise ManifestError(f'Not found any manifest in {plugin_path}')

    # TODO
    manifest = manifest_cache[0][0]
    caller_info = manifest_cache[0][1]
    plugin = Plugin(manifest['id'], **manifest)
    plugin.location = str(Path(caller_info.filename).parent)
    return plugin


def get_plugin_storage():
    """
    Get plugins storage dir path

    :return: ~/.lyrebird/plugins/<plugin_name>
    """
    info = _caller_info(index=2)
    storage_name = info.top_module_name
    application_conf_dir = os.path.join(os.path.expanduser('~'), '.lyrebird')
    plugin_storage_dir = os.path.abspath(os.path.join(application_conf_dir, 'plugins/%s' % storage_name))
    if not os.path.exists(plugin_storage_dir):
        os.makedirs(plugin_storage_dir)
    return plugin_storage_dir


def _caller_info(index=1):
    stack = inspect.stack()
    caller_module = inspect.getmodule(stack[index].frame)
    caller_module_name = caller_module.__name__
    if caller_module_name.find('.') > 0:
        caller_top_module_name = caller_module_name.split('.')[0]
    else:
        caller_top_module_name = caller_module_name
    CallerInfo = namedtuple('CallerInfo', 'top_module_name module_name')
    return CallerInfo(module_name=caller_module_name, top_module_name=caller_top_module_name)
