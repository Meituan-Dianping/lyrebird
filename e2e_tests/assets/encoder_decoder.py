from lyrebird import encoder, decoder

TITLE = 'test_encoder_decoder'

RULE = {
    'request.url': '',
}


@decoder(rules = RULE, rank = 1)
def test_decoder(flow):
    print(flow['request']['url'])


@encoder(rules = RULE, rank = 1)
def test_encoder(flow):
    print(flow['request']['url'])
