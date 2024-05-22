from lyrebird import application
from lyrebird.log import get_logger
from pathlib import Path
from copy import deepcopy
from importlib import machinery
import traceback
import datetime
import signal
from lyrebird.base_server import ProcessServer
from concurrent.futures import ThreadPoolExecutor
from lyrebird import application
from lyrebird.compatibility import prepare_application_for_monkey_patch, monkey_patch_application


logger = get_logger()

class Reporter(ProcessServer):

    def __init__(self):
        super().__init__()
        self.scripts = []
        self.workspace = application.config.get('reporter.workspace')
        self.report_queue = application.sync_manager.get_multiprocessing_queue()
        if not self.workspace:
            logger.debug(f'reporter.workspace not set.')
        elif not application.config.get('enable_multiprocess', False):
            self.scripts = self._read_reporter(self.workspace)
            logger.debug(f'Load statistics scripts {self.scripts}')

    def _read_reporter(self, workspace):
        target_dir = Path(workspace)
        scripts = []
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
                loader = machinery.SourceFileLoader('reporter_script', str(report_script_file))
                _script_module = loader.load_module()
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
            scripts.append(_script_module.report)
        return scripts
    
    def start(self):
        if not application.config.get('enable_multiprocess', False):
            return
        self.process_namespace = prepare_application_for_monkey_patch()
        self.async_obj['report_queue'] = self.report_queue
        self.async_obj['workspace'] = self.workspace
        self.async_obj['process_namespace'] = self.process_namespace
        super().start()

    def run(self, async_obj, config, *args, **kwargs):

        signal.signal(signal.SIGINT, signal.SIG_IGN)

        workspace = async_obj['workspace']
        reportor_queue = async_obj['report_queue']

        monkey_patch_application(async_obj)
        scripts = self._read_reporter(workspace)

        self.thread_executor = ThreadPoolExecutor(max_workers=10)

        self.running = True

        while self.running:
            try:
                data = reportor_queue.get()
                if not data:
                    break
                new_data = deepcopy(data)
                for script in scripts:
                    try:
                        self.thread_executor.submit(script, new_data)
                    except Exception:
                        print(f'Send report failed:\n{traceback.format_exc()}')
            except Exception:
                logger.error(f'Reporter run error:\n{traceback.format_exc()}')

    def report(self, data):
        if self.running:
            self.report_queue.put(data)
        else:
            task_manager = application.server.get('task')

            def send_report():
                new_data = deepcopy(data)
                for script in self.scripts:
                    try:
                        script(new_data)
                    except Exception:
                        logger.error(f'Send report failed:\n{traceback.format_exc()}')
            task_manager.add_task('send-report', send_report)


def _page_out():

    if hasattr(application.sync_namespace,'last_page') and hasattr(application.sync_namespace,'last_page_in_time'):
        duration = (datetime.datetime.now() - application.sync_namespace.last_page_in_time).total_seconds()
        application.server['event'].publish('system', {
            'system': {
                'action': 'page.out', 'page': application.sync_namespace.last_page, 'duration': duration
            }
        })

        # TODO remove below
        application.reporter.report({
            'action': 'page.out',
            'page': application.sync_namespace.last_page,
            'duration': duration
        })


def page_in(name):
    _page_out()

    application.server['event'].publish('system', {
        'system': {'action': 'page.in', 'page': name}
    })

    # TODO remove below
    application.reporter.report({
        'action': 'page.in',
        'page': name
    })

    application.sync_namespace.last_page = name
    application.sync_namespace.last_page_in_time = datetime.datetime.now()


def start():
    application.sync_namespace.lyrebird_start_time = datetime.datetime.now()
    application.server['event'].publish('system', {
        'system': {'action': 'start'}
    })

    # TODO remove below
    application.reporter.report({
        'action': 'start'
    })


def stop():
    _page_out()
    duration = (datetime.datetime.now() - application.sync_namespace.lyrebird_start_time).total_seconds()
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
