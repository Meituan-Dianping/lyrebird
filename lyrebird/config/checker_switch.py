from lyrebird import application


class SettingCheckerSwitch:

    @staticmethod
    def apply(config, is_remove=False):
        checker_id_set = set(config.keys()) | set(application.checkers.keys())
        for checker_id in checker_id_set:
            if checker_id not in application.checkers:
                continue

            config_status = config.get(checker_id)
            if config_status is None:
                continue
            target_config_status = not config_status if is_remove else config_status

            context_status = application.checkers[checker_id].activated
            if target_config_status == context_status:
                continue

            checker = application.checkers[checker_id]
            checker.activate() if target_config_status else checker.deactivate()
