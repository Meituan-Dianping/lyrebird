from lyrebird import encoder, decoder

TITLE = 'test_encoder_decoder'

RULE = {
    'request.url': 'encoder_decoder',
}


@decoder(rules = RULE, rank = 1)
def test_decoder(flow):
    flow['request']['headers']['test_encoder_decoder'] = "decode"


@encoder(rules = RULE, rank = 1)
def test_encoder(flow):
    flow['request']['headers']['test_encoder_decoder'] = 'encode'
