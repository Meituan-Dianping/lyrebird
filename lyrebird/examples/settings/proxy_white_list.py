import re
from hashlib import md5
from lyrebird import application
from lyrebird.settings import SettingsTemplate

class WhiteListSettings(SettingsTemplate):

    def __init__(self):
        super().__init__()
        self.display = True
        self.name = 'proxy_white_list'
        self.title = 'Request Proxy Blacklist and Whitelist Settings'
        self.notice = 'Control requests entering Lyrebird proxy logic. Filtered requests cannot use Mock, Checker, Modifier, and other features'
        self.submit_text = 'Submit'
        self.language = 'en'
        self.category = 'Request Proxy'
        self.category_md5 = md5(self.category.encode(encoding='UTF-8')).hexdigest()
        self.switch = True
        self.ori_filters = application.config.get('proxy.filters', [])
        self.is_simple_url = re.compile(r'^[a-zA-Z0-9./:_-]+$')
        self.is_balck_and_white = re.compile(r'(?=^\(\?=.*\))(?=.*\(\?!.*\)$)')
        self.is_balck = re.compile(r'^\(\?=.*\)$')
        self.is_white = re.compile(r'^\(\?!.*\)$')
        self.DEFAULT_WHITE_LIST = []
        self.DEFAULT_BLACK_LIST = []

    def getter(self):
        filters = self.get_config_by_application()
        url_black, suffix_black = self.get_suffix_black_list(filters['black'])
        proxy_white_list_switch = {
            'name': 'proxy_white_list_switch',
            'title': 'Configuration Switch',
            'subtitle': 'Enable/Disable this configuration',
            'category': 'bool',
            'data': self.switch
        }
        white_list = {
            'name': 'white_list',
            'title': 'Request Whitelist',
            'subtitle': 'Allow requests with specific text in host and path to use Lyrebird proxy',
            'category': 'list',
            'data': filters['white']
        }
        black_list = {
            'name': 'black_list',
            'title': 'Request Blacklist',
            'subtitle': 'Prohibit requests with specific text in host and path from using Lyrebird proxy',
            'category': 'list',
            'data': url_black
        }
        black_suffix = {
            'name': 'black_suffix',
            'title': 'File Type Blacklist',
            'subtitle': 'Globally filter specific types of resource requests, such as png, zip, etc.',
            'category': 'list',
            'data': suffix_black
        }
        regular_list = {
            'name': 'regular_list',
            'title': 'Additional Regular Expressions',
            'subtitle': 'If the above blacklist and whitelist are not sufficient, you can write your own regular expressions. Note: The regular expressions are in OR logic, i.e., if any regex matches, the proxy will be triggered',
            'category': 'list',
            'data': filters['regular']
        }
        return [proxy_white_list_switch, white_list, black_list, black_suffix, regular_list]

    def setter(self, data):
        self.switch = bool(data['proxy_white_list_switch'])
        if self.switch:
            self.apply_config(data)
            self.save(data)
        else:
            application.config['proxy.filters'] = self.ori_filters

    def load_prepared(self):
        personal_config = self.manager.get_config(self).get('data')
        self.ori_filters = application.config.get('proxy.filters', [])
        have_config = False
        for name, item in personal_config.items():
            if name == 'proxy_white_list_switch':
                self.switch = bool(item)
            else:
                have_config |= bool(item)
        if have_config and self.switch:
            self.apply_config(personal_config)

    def apply_config(self, data):
        filter_list = []
        new_reg = ''
        white_reg = ''
        black_reg = []
        if data['regular_list']:
            filter_list.extend(data['regular_list'])
        if data['white_list']:
            white_reg = '|'.join(data['white_list'])
        if data['black_list']:
            black_reg.append('|'.join(data['black_list']))
        if data['black_suffix']:
            black_reg.append('|'.join(data['black_suffix']))

        if white_reg:
            new_reg = f'(?=.*({white_reg}))'
        else:
            new_reg = f'(?=.*({"|".join(self.DEFAULT_WHITE_LIST)}))'
        if black_reg:
            new_reg += f'(^((?!({"|".join(black_reg)})).)*$)'
        else:
            new_reg += f'(^((?!({"|".join(self.DEFAULT_BLACK_LIST)})).)*$)'
        filter_list.append(new_reg)
        application.config['proxy.filters'] = filter_list

    def save(self, data):
        self.manager.write_config(self, {'data': data})

    def split_regex(self, regex):
        white = []
        black = []

        if '(?=' in regex or '(?!' in regex:
            positive_parts = re.findall(r'\(\?=.*?\((.*?)\)\)', regex)
            negative_parts = re.findall(r'\(\?!.*?\((.*?)\)\)', regex)
            
            if positive_parts:
                for part in positive_parts:
                    white.extend(part.split('|'))
            else:
                single_positive = re.findall(r'\(\?=.*?([\w|]+)\)', regex)
                if single_positive:
                    white.extend(single_positive[0].split('|'))
            
            if negative_parts:
                for part in negative_parts:
                    black.extend(part.split('|'))
            else:
                single_negative = re.findall(r'\(\?!.*?([\w|.]+)\)', regex)
                if single_negative:
                    black.extend(single_negative[0].split('|'))

        white = [p for p in white if p.strip()]
        black = [n for n in black if n.strip()]

        return white, black

    def get_config_by_application(self):
        ori_filters = application.config.get('proxy.filters', [])
        white_list = []
        black_list = []
        regular_list = []
        for pattern in ori_filters:
            if self.is_simple_url.match(pattern):
                white_list.append(pattern)
            # Split into three judgments, limit the beginning and end, avoid complex regex misfires.
            elif self.is_balck_and_white.match(pattern) or self.is_white.match(pattern) or self.is_balck.match(pattern):
                res_white, res_black = self.split_regex(pattern)
                white_list.extend(res_white)
                black_list.extend(res_black)
            else:
                regular_list.append(pattern)

        white_list = list(set(white_list))
        black_list = list(set(black_list))
        regular_list = list(set(regular_list))

        return {
            'white': white_list,
            'black': black_list,
            'regular': regular_list
        }

    def get_suffix_black_list(self, black_list):
        url_black_list = [item for item in black_list if not (item.startswith('.') and item.count('.') == 1)]
        suffix_black_list = [item for item in black_list if item.startswith('.') and item.count('.') == 1]
        return url_black_list, suffix_black_list
