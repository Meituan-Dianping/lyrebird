import json
from lyrebird.log import get_logger


logger = get_logger()
class DuplicateHeaderKeyHandler:

    @staticmethod
    def set_origin_header(origin_header, flow_header):
        if not flow_header:
            return

        raw_header = DuplicateHeaderKeyHandler.flow2origin(flow_header)
        header_dict = dict()
        for key, value in raw_header:
            if key.lower() != 'set-cookie':
                continue
            if key not in header_dict:
                header_dict[key] = []
            header_dict[key].append(value)
        
        for key, value_list in header_dict.items():
            origin_header.remove(key)
            for value in value_list:
                origin_header.add_header(key, value)

    @staticmethod
    def origin2flow(raw_header):
        if not raw_header:
            return
        temp_header_dict = dict()
        for key, value in raw_header.items():
            if key not in temp_header_dict:
                temp_header_dict[key] = []
            temp_header_dict[key].append(value)
        
        header_dict = dict()
        for key, value_list in temp_header_dict.items():
            if key.lower() in trans_key_handlers:
                encode_func = trans_key_handlers.get(key.lower()).get('encode')
                encode_func(header_dict, key, value_list)
            else:
                header_dict[key] = value_list[0]
        
        return header_dict

    @staticmethod
    def flow2origin(header_dict):
        if not header_dict:
            return
        header_list = []
        for key, value in header_dict.items():
            if key.lower() in trans_key_handlers:
                decode_func = trans_key_handlers.get(key.lower()).get('decode')
                decode_func(header_list, key, value)
            else:
                header_list.append((key, value))
        return header_list
    
    @staticmethod
    def _to_json_string(header_dict, key, value_list):
        if len(value_list) == 1:
            header_dict[key] = value_list[0]
        else:
            header_dict[key] = json.dumps(value_list)
    
    @staticmethod
    def _to_json_object(header_list, key, value):
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


trans_key_handlers = {
    'set-cookie': {
        'encode': DuplicateHeaderKeyHandler._to_json_string,
        'decode': DuplicateHeaderKeyHandler._to_json_object
    }
}
