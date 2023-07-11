from lyrebird import application
from lyrebird.log import get_logger


logger = get_logger()


class SettingCheckerSwitch:

    @staticmethod
    def add(config):
        checker_id_set = set(config.keys()) | set(application.checkers.keys())
        for checker_id in checker_id_set:
            if checker_id not in application.checkers:
                logger.error(f'Extension {checker_id} in mock data not found! ')
                continue

            checker = application.checkers[checker_id]
            config_status = config.get(checker_id)
            if config_status is None:
                continue

            SettingCheckerSwitch.handle_checker(checker, config_status)

    @staticmethod
    def remove(config):
        checker_id_set = set(config.keys()) | set(application.checkers.keys())
        for checker_id in checker_id_set:
            if checker_id not in application.checkers:
                continue

            checker = application.checkers[checker_id]
            config_status = config.get(checker_id)
            if not config_status:
                continue
            SettingCheckerSwitch.handle_checker(checker, not config_status)

    @staticmethod
    def handle_checker(checker, target_status):
        context_status = checker.activated
        if target_status == context_status:
            return

        checker.activate() if target_status else checker.deactivate()
