from lyrebird import application
from lyrebird.log import get_logger
from pathlib import Path
from copy import deepcopy
import imp
import traceback
import datetime


logger = get_logger()


class Reporter:

    def __init__(self):
        self.scripts = []
        workspace = application.config.get('reporter.workspace')
        if not workspace:
            logger.debug(f'reporter.workspace not set.')
        else:
            self._read_reporter(workspace)
            logger.debug(f'Load statistics scripts {self.scripts}')

    def _read_reporter(self, workspace):
        target_dir = Path(workspace)
        if not target_dir.exists():
            logger.error('Reporter workspace not found')
        for report_script_file in target_dir.iterdir():
            if report_script_file.name.startswith('_'):
                continue
            if not report_script_file.is_file():
                logger.warning(f'Skip report script: is not a file, {report_script_file}')
                continue
            if report_script_file.suffix != '.py':
                logger.warning(f'Skip report script: is not a python file, {report_script_file}')
                continue
            try:
                _script_module = imp.load_source('reporter_script', str(report_script_file))
            except Exception:
                logger.warning(
                    f'Skip report script: load script failed, {report_script_file}\n{traceback.format_exc()}')
                continue
            if not hasattr(_script_module, 'report'):
                logger.warning(f'Skip report script: not found a report method in script, {report_script_file}')
                continue
            if not callable(_script_module.report):
                logger.warning(f'Skip report script: report method not callable, {report_script_file}')
                continue
            self.scripts.append(_script_module.report)

    def report(self, data):
        task_manager = application.server.get('task')

        def send_report():
            new_data = deepcopy(data)
            for script in self.scripts:
                try:
                    script(new_data)
                except Exception:
                    logger.error(f'Send report failed:\n{traceback.format_exc()}')
        task_manager.add_task('send-report', send_report)


last_page = None
last_page_in_time = None
lyrebird_start_time = None


def _page_out():
    global last_page
    global last_page_in_time

    if last_page and last_page_in_time:
        duration = (datetime.datetime.now() - last_page_in_time).total_seconds()
        application.server['event'].publish('system', {
            'system': {
                'action': 'page.out', 'page': last_page, 'duration': duration
            }
        })

        # TODO remove below
        application.reporter.report({
            'action': 'page.out',
            'page': last_page,
            'duration': duration
        })


def page_in(name):
    _page_out()

    global last_page
    global last_page_in_time

    application.server['event'].publish('system', {
        'system': {'action': 'page.in', 'page': name}
    })

    # TODO remove below
    application.reporter.report({
        'action': 'page.in',
        'page': name
    })

    last_page = name
    last_page_in_time = datetime.datetime.now()


def start():
    global lyrebird_start_time
    lyrebird_start_time = datetime.datetime.now()
    application.server['event'].publish('system', {
        'system': {'action': 'start'}
    })

    # TODO remove below
    application.reporter.report({
        'action': 'start'
    })


def stop():
    _page_out()
    duration = (datetime.datetime.now() - lyrebird_start_time).total_seconds()
    application.server['event'].publish('system', {
        'system': {
            'action': 'stop',
            'duration': duration
        }
    })

    # TODO remove below
    application.reporter.report({
        'action': 'stop',
        'duration': duration
    })
