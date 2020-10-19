from copy import deepcopy
from lyrebird import application
from .function_executor import FunctionExecutor


class EncoderDecoder(FunctionExecutor):
    def __init__(self):
        self.encoder = application.encoder
        self.decoder = application.decoder

    def encoder_handler(self, flow, output=None):
        matched_funcs = EncoderDecoder._get_matched_handler(self.encoder, flow)
        if output == None:
            EncoderDecoder._func_handler(matched_funcs, flow, handler_name='encoder_decoder')
            return

        if not matched_funcs:
            output.update(flow)
            return

        new_flow = deepcopy(flow)
        EncoderDecoder._func_handler(matched_funcs, new_flow, handler_name='encoder_decoder')
        output.update(new_flow)

    def decoder_handler(self, flow, output=None):
        matched_funcs = EncoderDecoder._get_matched_handler(self.decoder, flow)
        if output == None:
            EncoderDecoder._func_handler(matched_funcs, flow, handler_name='encoder_decoder')
            return

        if not matched_funcs:
            output.update(flow)
            return

        new_flow = deepcopy(flow)
        EncoderDecoder._func_handler(matched_funcs, new_flow, handler_name='encoder_decoder')
        output.update(new_flow)
