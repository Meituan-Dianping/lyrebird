from lyrebird import event
import time

TITLE = 'test_encoder_decoder'
CHECKER_TIME = 0.5

@event('test')
def test_decoder(flow):
    time.sleep(CHECKER_TIME)
