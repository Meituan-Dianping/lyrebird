from click import secho


installer = {
}


def install(extension_name):
    global installer
    install_func = installer.get(extension_name)
    if install_func:
        install_func()
    else:
        secho(f'Install failed. extension "{extension_name}" not found.')
