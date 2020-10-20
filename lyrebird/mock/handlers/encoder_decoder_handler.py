from copy import deepcopy
from lyrebird import application
from .function_executor import FunctionExecutor


class EncoderDecoder(FunctionExecutor):
    def __init__(self):
        self.encoder = application.encoder
        self.decoder = application.decoder

    def encoder_handler(self, flow, output=None):
        matched_funcs = EncoderDecoder.get_matched_handler(self.encoder, flow)
        if output == None:
            EncoderDecoder.func_handler(matched_funcs, flow, handler_type='encoder')
            return

        if not matched_funcs:
            output.update(flow)
            return

        new_flow = deepcopy(flow)
        EncoderDecoder.func_handler(matched_funcs, new_flow, handler_type='encoder')
        output.update(new_flow)

    def decoder_handler(self, flow, output=None):
        matched_funcs = EncoderDecoder.get_matched_handler(self.decoder, flow)
        if output == None:
            EncoderDecoder.func_handler(matched_funcs, flow, handler_type='decoder')
            return

        if not matched_funcs:
            output.update(flow)
            return

        new_flow = deepcopy(flow)
        EncoderDecoder.func_handler(matched_funcs, new_flow, handler_type='decoder')
        output.update(new_flow)
