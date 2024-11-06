import re
import json
from hashlib import md5
from lyrebird import application, get_logger
from lyrebird.settings import SettingsTemplate

logger = get_logger()

DEFAULT_WHITE_LIST = []
DEFAULT_BLACK_LIST = []

class WhiteListSettings(SettingsTemplate):

    def __init__(self):
        super().__init__()
        self.display = True
        self.name = 'proxy_white_list'
        self.title = 'Proxy Whitelist and Blacklist Settings'
        self.notice = 'Controls requests entering Lyrebird proxy logic. Requests filtered out cannot use Mock, Checker, Modifier, etc.'
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


    def getter(self):
        filters = self.get_config_by_application()
        url_black, suffix_black = self.get_suffix_black_list(filters['black'])
        proxy_white_list_switch = {
            'name': 'proxy_white_list_switch',
            'title': 'Configuration Switch',
            'subtitle': 'Switch for this configuration to take effect, revert to default settings when turned off',
            'category': 'bool',
            'data': self.switch
        }
        white_list = {
            'name': 'white_list',
            'title': 'Request Whitelist',
            'subtitle': 'Allows requests with specific text in host and path to use Lyrebird proxy',
            'category': 'list',
            'data': filters['white']
        }
        black_list = {
            'name': 'black_list',
            'title': 'Request Blacklist',
            'subtitle': 'Blocks requests with specific text in host and path from using Lyrebird proxy',
            'category': 'list',
            'data': url_black
        }
        black_suffix = {
            'name': 'black_suffix',
            'title': 'File Type Blacklist',
            'subtitle': 'Globally filters requests of specified resource types, such as png, zip, etc.',
            'category': 'list',
            'data': suffix_black
        }
        regular_list = {
            'name': 'regular_list',
            'title': 'Additional Regex',
            'subtitle': 'If the above whitelists and blacklists do not meet the needs, you can write regular expressions yourself. Note: The logic between regexes is OR, meaning as long as any regex matches, it will hit the proxy',
            'category': 'list',
            'data': filters['regular']
        }
        return [proxy_white_list_switch, white_list, black_list, black_suffix, regular_list]

    def setter(self, data):
        self.switch = bool(data['proxy_white_list_switch'])
        self.apply_config(data)
        self.save(data)
        if not self.switch:
            application.config['proxy.filters'] = self.ori_filters

    def restore(self):
        self.save({})
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
            new_reg = f'(?=.*({"|".join(DEFAULT_WHITE_LIST)}))'
        if black_reg:
            new_reg += f'(^(?!.*({"|".join(black_reg)})))'
        else:
            new_reg += f'(^(?!.*({"|".join(DEFAULT_BLACK_LIST)})))'
        filter_list.append(new_reg)
        application.config['proxy.filters'] = filter_list
        logger.warning(f'application.config is updated by proxy_white_list_switch, \nkey: \nproxy.filters \nvalue: \n{json.dumps(filter_list, ensure_ascii=False, indent=4)}')

    def save(self, data):
        self.manager.write_config(self, {'data': data})

    def split_regex(self, regex):
        white = []
        black = []

        if '(?=' in regex or '(?!' in regex:
            positive_parts = re.findall(r'\(\?=\.\*\(?(.*?)\)?\)', regex)
            negative_parts = re.findall(r'\(\?!\.\*\(?(.*?)\)?\)', regex)

            if positive_parts:
                for part in positive_parts:
                    white.extend(part.split('|'))

            if negative_parts:
                for part in negative_parts:
                    black.extend(part.split('|'))

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
