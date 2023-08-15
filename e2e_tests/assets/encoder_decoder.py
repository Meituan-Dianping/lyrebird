from lyrebird import encoder, decoder

TITLE = 'test_encoder_decoder'

RULE = {
    'request.path': 'encoder_decoder',
}


@decoder(rules = RULE, rank = 1)
def test_decoder(flow):
    flow['request']['data']['word'] = flow['request']['data']['word'].encode().decode('unicode_escape')


@encoder(rules = RULE, rank = 1)
def test_encoder(flow):
    flow['request']['data']['word'] = flow['request']['data']['word'].encode('unicode_escape').decode()
