import json
from flask import Response
from lyrebird.mock import lb_http_status
from lyrebird.log import get_logger


logger = get_logger()
class DuplicateHeaderKeyHandler:

    @staticmethod
    def recover_duplicate_key(header, raw_header):
        if not raw_header:
            return

        header_dict = dict()
        for key, value in raw_header:
            if key.lower() != 'set-cookie':
                continue
            if key not in header_dict:
                header_dict[key] = []
            header_dict[key].append(value)
        
        for key, value_list in header_dict.items():
            header.remove(key)
            for value in value_list:
                header.add_header(key, value)

    @staticmethod
    def format_header_distinct_key(raw_header):
        if not raw_header:
            return
        temp_header_dict = dict()
        for key, value in raw_header.items():
            if key not in temp_header_dict:
                temp_header_dict[key] = []
            temp_header_dict[key].append(value)
        
        header_dict = dict()
        for key, value_list in temp_header_dict.items():
            if key.lower() == 'set-cookie':
                DuplicateHeaderKeyHandler._trans_header_key_duplicate_to_distinct(header_dict, key, value_list)
            else:
                header_dict[key] = value_list[0]
        
        return header_dict

    @staticmethod
    def format_header_duplicate_key(header_dict):
        if not header_dict:
            return
        header_list = []
        for key, value in header_dict.items():
            if key.lower() == 'set-cookie':
                DuplicateHeaderKeyHandler._trans_header_key_distinct_to_duplicate(header_list, key, value)
            else:
                header_list.append((key, value))
        return header_list
    
    @staticmethod
    def _trans_header_key_duplicate_to_distinct(header_dict, key, value_list):
        if len(value_list) == 1:
            header_dict[key] = value_list[0]
        else:
            header_dict[key] = json.dumps(value_list)
    
    @staticmethod
    def _trans_header_key_distinct_to_duplicate(header_list, key, value):
        try:
            raw_value = json.loads(value)
        except:
            # as a string
            raw_value = value
        if type(raw_value) == list:
            for value in raw_value:
                header_list.append((key, value))
        else:
            header_list.append((key, raw_value))

