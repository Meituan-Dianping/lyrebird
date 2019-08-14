import imp
import inspect
from pathlib import Path

import pkg_resources
import setuptools

from ..log import get_logger
from .plugin import Plugin

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
            ]
        )
    """
    caller_info = inspect.stack()[1]
    manifest_cache.append((options, caller_info))


def load_all_from_ep():
    plugins = {}
    # Load plugin from installed packages by entry point 'lyrebird_plugin'
    for ep in pkg_resources.iter_entry_points(PLUGIN_ENTRY_POINT):
        try:
            plugin = load_plugin_from_ep(ep)
            if plugin.project_name in plugins:
                logger.error('Load plugin failed: More than one manifest in this plugin')
                continue
        except ManifestError as e:
            logger.error(f'Load plugin failed: {e}')
            continue
        plugins[plugin.project_name] = plugin
    return plugins


def load_plugin_from_ep(ep):
    global manifest_cache
    manifest_cache=[]

    ep_instance = ep.load()

    # There can only be one manifest in each plugin
    if len(manifest_cache)>1:
        raise ManifestError('More than one manifest in this plugin')
    if len(manifest_cache)==0:
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
    packages = setuptools.find_packages(plugin_path)
    for pkg in packages:
        manifest_file = Path(plugin_path)/pkg/'manifest.py'
        if not manifest_file.exists():
            continue
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
