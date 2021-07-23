from lyrebird import utils

def test_case_insenstive_dict():
    test_dict = utils.CaseInsensitiveDict({'Content-Type':'LBTests'})
    assert test_dict.get('Content-Type') == 'LBTests'
    assert test_dict.get('content-type') == 'LBTests'
    test_dict = utils.CaseInsensitiveDict({'content-type':'LBTests'})
    assert test_dict.get('Content-Type') == 'LBTests'
    assert test_dict.get('content-type') == 'LBTests'
