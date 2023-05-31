from lyrebird import application


class SettingCheckerSwitch:

    @staticmethod
    def add(config):
        checker_id_set = set(config.keys()) | set(application.checkers.keys())
        for checker_id in checker_id_set:
            checker = application.checkers[checker_id]
            if checker_id not in application.checkers:
                continue

            config_status = config.get(checker_id)
            if config_status is None:
                continue

            SettingCheckerSwitch.handle_checker(checker, config_status)

    @staticmethod
    def remove(config):
        checker_id_set = set(config.keys()) | set(application.checkers.keys())
        for checker_id in checker_id_set:
            checker = application.checkers[checker_id]
            if checker_id not in application.checkers:
                continue

            config_status = config.get(checker_id)
            if config_status is None:
                continue
            SettingCheckerSwitch.handle_checker(checker, not config_status)

    @staticmethod
    def handle_checker(checker, target_status):
        context_status = checker.activated
        if target_status == context_status:
            return

        checker.activate() if target_status else checker.deactivate()
