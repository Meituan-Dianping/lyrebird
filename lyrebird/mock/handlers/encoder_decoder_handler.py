from copy import deepcopy
from lyrebird import application
from lyrebird.log import get_logger
from .flow_editor_handler import FlowEditorHandler

logger = get_logger()


class EncoderDecoder:
    def __init__(self):
        self.encoder = application.encoder
        self.decoder = application.decoder

    def encoder_handler(self, flow, output=None):
        matched_funcs = FlowEditorHandler._get_matched_handler(self.encoder, flow)
        if output == None:
            FlowEditorHandler._func_handler(matched_funcs, flow)
            return

        if not matched_funcs:
            output.update(flow)
            return

        new_flow = deepcopy(flow)
        FlowEditorHandler._func_handler(matched_funcs, new_flow)
        output.update(new_flow)

    def decoder_handler(self, flow, output=None):
        matched_funcs = FlowEditorHandler._get_matched_handler(self.decoder, flow)
        if output == None:
            FlowEditorHandler._func_handler(matched_funcs, flow)
            return

        if not matched_funcs:
            output.update(flow)
            return

        new_flow = deepcopy(flow)
        FlowEditorHandler._func_handler(matched_funcs, new_flow)
        output.update(new_flow)

encoders_decoders = EncoderDecoder()
