from lyrebird import application
from lyrebird.log import get_logger
from pathlib import Path
import imp
import subprocess
import sys
import os
import datetime
import getpass
from lyrebird.version import VERSION


logger = get_logger()


class Reporter:

    def __init__(self):
        self.scripts = []
        self.base_data = self._base_data()
        workspace = application.config.get('reporter.workspace')
        self._read_reporter(workspace)
        logger.debug(f'Load statistics scripts {self.scripts}')

    def _read_reporter(self, workspace):
        target_dir = Path(workspace)
        target_dir.stem
        if not target_dir.exists():
            logger.error('Reporter workspace not found')
        for report_script_file in target_dir.iterdir():
            if not report_script_file.is_file():
                continue
            if report_script_file.suffix != '.py':
                continue
            try:
                _script_module = imp.load_source('reporter_script', str(report_script_file))
            except Exception:
                continue
            if not hasattr(_script_module, 'report'):
                continue
            if not callable(_script_module.report):
                continue
            self.scripts.append(_script_module)

    def report(self, data):
        report_data = self.base_data.update(data)
        task_manager = application.server.get('task')

        def send_report():
            for script in self.scripts:
                script.report(report_data)
        task_manager.add_task('send-report', send_report)

    def _base_data(self):
        user_name = subprocess.run('git config user.name', shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
        user_email = subprocess.run('git config user.email', shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
        _env = {
            'username': getpass.getuser(),
            'platform': sys.platform,
            'version': sys.version,
            'argv': sys.argv,
            'git.user_name': user_name,
            'git.user_email': user_email,
            'pid': os.getpid()
        }
        return {
            'reporter': 'lyrebird',
            'version': VERSION,
            'env': _env
        }


last_page = None
last_page_in_time = None
lyrebird_start_time = None


def _page_out():
    global last_page
    global last_page_in_time

    if last_page and last_page_in_time:
        duration = datetime.datetime.now() - last_page_in_time
        application.reporter.report({
            'action': 'page.out',
            'page': last_page,
            'duration': duration.total_seconds()
        })


def page_in(name):
    _page_out()

    global last_page
    global last_page_in_time

    application.reporter.report({
        'action': 'page.in',
        'page': name
    })

    last_page = name
    last_page_in_time = datetime.datetime.now()


def start():
    global lyrebird_start_time
    lyrebird_start_time = datetime.datetime.now()
    application.reporter.report({
        'action': 'start'
    })


def stop():
    _page_out()
    application.reporter.report({
        'action': 'stop',
        'duration': (datetime.datetime.now() - lyrebird_start_time).total_seconds()
    })
