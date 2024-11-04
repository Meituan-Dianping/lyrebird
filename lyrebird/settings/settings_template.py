from hashlib import md5
from lyrebird import application

class SettingsTemplate:

    def __init__(self):
        self.display = True
        self.name = ''
        self.setting_items = []
        self.title = ''
        self.notice = ''
        self.submit_text = ''
        self.language = ''
        self.category = ''
        self.category_md5 = md5(self.category.encode(encoding='UTF-8')).hexdigest()
        self.manager = application.server['settings']

    def getter(self):
        pass

    def setter(self, data):
        pass

    def restore(self):
        pass

    def destory(self):
        pass

    def load_finished(self):
        pass

    def load_prepared(self):
        pass

class SettingItemTemplate:
    def __init__(self):
        self.name = ''
        self.title = ''
        self.subtitle = ''
        # enum, value should in {'list', 'dict', 'text', 'selector'}
        self.category = ''
        # only used in selector
        self.options = []
    
    def get_data(self):
        template_res = {
                        'name': self.name,
                        'title': self.title,
                        'subtitle': self.subtitle,
                        'category': self.category,
                        'data': '',
                        'options': self.options
                    }
        return template_res

    def set_data(self):
        return True
