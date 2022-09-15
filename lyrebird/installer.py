from lyrebird.mitm.proxy_server import LyrebirdProxyServer
from click import secho


def install_mitm():
    LyrebirdProxyServer().download_mitmproxy()


installer = {
    'mitm': install_mitm
}


def install(extension_name):
    global installer
    install_func = installer.get(extension_name)
    if install_func:
        install_func()
    else:
        secho(f'Install failed. extension "{extension_name}" not found.')
