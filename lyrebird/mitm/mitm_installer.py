import sys
import click
import shutil
import requests
import tarfile
import tempfile
from pathlib import Path
from lyrebird import log
from lyrebird import application

logger = log.get_logger()


class UnsupportedPlatform(Exception):
    pass


class MITMNotFound(Exception):
    pass


def show_mitmdump_help():
    proxy_port = application.config['proxy.port']
    errmsg = f'Init mitmproxy failed.\nCan\'t start HTTP proxy server on {proxy_port}\nPlease install mitmproxy(https://mitmproxy.org/) and restart lyrebird\nOr using --no-mitm option for skip starting mitmproxy server\n'
    logger.error(errmsg)
    return errmsg


def get_mitmdump_filename():
    platform = sys.platform
    if platform in ['linux', 'darwin']:
        return 'mitmdump'
    elif platform.startswith('win'):
        return 'mitmdump.exe'
    else:
        raise UnsupportedPlatform(f'platform name: {platform}')


def find_mitmdump_in_path():
    mitmdump_path = shutil.which('mitmdump')
    if not mitmdump_path:
        return None

    mitmdump = Path(mitmdump_path)
    if mitmdump.exists() and mitmdump.is_file():
        return mitmdump
    else:
        return None


def find_mitmdump_in_lyrebird_home():
    mitmdump = Path('~/.lyrebird/bin').expanduser().absolute()/get_mitmdump_filename()
    if mitmdump.exists() and mitmdump.is_file():
        return mitmdump
    else:
        return None


def download_mitmproxy():
    '''
    Download mitmdump 8.1.1 from mitmproxy.org
    New file will be write in to ~/.lyrebird/bin
    Support Window Linux and OSX
    '''
    platform = sys.platform
    if platform == 'linux':
        download_url = 'https://snapshots.mitmproxy.org/8.1.1/mitmproxy-8.1.1-linux.tar.gz'
    elif platform == 'darwin':
        download_url = 'https://snapshots.mitmproxy.org/8.1.1/mitmproxy-8.1.1-osx.tar.gz'
    elif platform.startswith('win'):
        download_url = 'https://snapshots.mitmproxy.org/8.1.1/mitmproxy-8.1.1-windows.zip'
    else:
        raise UnsupportedPlatform(f'unsupport platform: {platform}')

    resp = requests.get(download_url, stream=True)
    content_length = int(resp.headers.get('content-length'))
    click.secho(f'\nmitmdump not found\nStart downloading mitmproxy: {download_url}')
    with click.progressbar(length=content_length) as bar, tempfile.NamedTemporaryFile('w+b') as tempf:
        for chunk in resp.iter_content(4*2048):
            tempf.write(chunk)
            bar.update(len(chunk))
        tempf.flush()
        tempf.seek(0)

        tarf = tarfile.open(fileobj=tempf.file)
        mitmdump_filename = get_mitmdump_filename()
        tarf.extract(mitmdump_filename, str(Path('~/.lyrebird/bin/').expanduser().absolute()))
        mitmdump_filepath = f'~/.lyrebird/bin/{mitmdump_filename}'
        click.secho(f'\n🍺 Download completed: write to {mitmdump_filepath}')
        return mitmdump_filepath


def init_mitm():
    # Find mitmproxy in sys path
    mitmdump_path = find_mitmdump_in_path()
    if not mitmdump_path:
        # Find mitmproxy in ~/.lyrebird/bin
        mitmdump_path = find_mitmdump_in_lyrebird_home()
    if not mitmdump_path:
        # Download mitmproxy and save in ~/.lyrebird/bin
        mitmdump_path = download_mitmproxy()
    if not mitmdump_path:
        # Start HTTP proxy server failed
        # mitmdump not found
        show_mitmdump_help()
        raise MITMNotFound
    return mitmdump_path
