import json


class EventFileConverter:
    
    def __init__(self, data, target_node=None):
        self.data = data
        self.target_node = target_node
        self.suffix = 'json'

    @property
    def filename(self):
        return f'{self.data["channel"]}_{self.data["id"]}.{self.suffix}'
    
    def convert(self):
        pass


class JSONFileNConverter(EventFileConverter):

    def __init__(self, data, target_node=None):
        super().__init__(data, target_node)
        self.suffix = 'json'
    
    def convert(self):
        # Covert common json to bytes
        target_json = self.data.get(self.target_node, {}) if self.target_node else self.data
        try:
            return bytes(json.dumps(target_json, indent=4, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            raise ConvertDataToStreamFail(e)


class FlowJSONFileConverter(JSONFileNConverter):

    def __init__(self, data):
        super().__init__(data, 'flow')


class ConvertDataToStreamFail(Exception):
    pass


EVENT_CONVERTER_MAP = {
    'flow_json': FlowJSONFileConverter,
    'json': JSONFileNConverter
}


def get_event_converter(event):
    converter = event.get('export').get('converter', 'json')
    return EVENT_CONVERTER_MAP.get(converter)(event)
     