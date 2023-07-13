from lyrebird.mock import context


class SettingDiffMode:

    @staticmethod
    def add(mode):
        context.application.is_diff_mode = mode

    @staticmethod
    def remove(mode):
        context.application.is_diff_mode = mode
