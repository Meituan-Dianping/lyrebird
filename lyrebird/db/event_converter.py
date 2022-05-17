import json
from io import BytesIO
from lyrebird.mock.dm.jsonpath import jsonpath


class EventFileConverter:
    
    def __init__(self, data, target_node_path=None):
        self.data = data
        self.target_node_path = target_node_path
        self.suffix = 'json'

    @property
    def filename(self):
        return f'{self.data["channel"]}_{self.data["id"]}.{self.suffix}'
    
    def convert(self):
        pass


class JSONFileNConverter(EventFileConverter):

    def __init__(self, data, target_node_path=None):
        super().__init__(data, target_node_path)
        self.suffix = 'json'
    
    def convert(self):
        # Covert common json to bytes
        target_nodes = jsonpath.search(self.data, self.target_node_path)
        if not target_nodes:
            raise ConvertDataToStreamFail('Cannot find target path: {self.target_node_path}')
        target_json = target_nodes[0].node
        try:
            return bytes(json.dumps(target_json, indent=4, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            raise ConvertDataToStreamFail(e)


class FlowJSONFileConverter(JSONFileNConverter):

    def __init__(self, data):
        super().__init__(data, 'flow')


class ConvertDataToStreamFail(Exception):
    pass


class ConverterNotSupport(Exception):
    pass


EVENT_CONVERTER_MAP = {
    'flow_json': FlowJSONFileConverter,
    'json': JSONFileNConverter
}


def get_event_converter(event):
    converter = event.get('export').get('converter')
    if not converter:
        raise ConverterNotSupport('Converter is None')
    event_converter = EVENT_CONVERTER_MAP.get(converter)
    if not event_converter:
        raise ConverterNotSupport(f'Converter "{converter}" is not supported.')
    return event_converter(event)


def _generator_export_stream(data_bytes):
    def generator():
        file_like_io = BytesIO(data_bytes)
        for item in file_like_io.readlines():
            yield item
        file_like_io.close()
    return generator


def export_from_event(event):
    converter = get_event_converter(event)
    filename = converter.filename
    data_bytes = converter.convert()
    return filename, _generator_export_stream(data_bytes)
     