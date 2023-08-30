from lyrebird import utils

def test_case_insenstive_dict():
    test_dict = utils.CaseInsensitiveDict({'Content-Type':'LBTests'})
    assert test_dict.get('Content-Type') == 'LBTests'
    assert test_dict.get('content-type') == 'LBTests'
    test_dict = utils.CaseInsensitiveDict({'content-type':'LBTests'})
    assert test_dict.get('Content-Type') == 'LBTests'
    assert test_dict.get('content-type') == 'LBTests'


def test_get_query_array():
    url_no_query = 'http://www.meituan.com'
    url_no_query_with_question_mark = 'http://www.meituan.com?'
    target_res = []
    assert utils.get_query_array(url_no_query) == target_res
    assert utils.get_query_array(url_no_query_with_question_mark) == target_res

    url_query_normal = 'http://www.meituan.com?a=1&b=2'
    url_query_multiple_equals_mark = 'http://www.meituan.com?a=1&b=2=3'
    url_query_key_value_blank = 'http://www.meituan.com?a=1&b=2&'
    target_res = ['a', '1', 'b', '2']
    assert utils.get_query_array(url_query_normal) == target_res
    assert utils.get_query_array(url_query_multiple_equals_mark) == target_res
    assert utils.get_query_array(url_query_key_value_blank) == target_res

    url_query_value_blank_no_equals_mark = 'http://www.meituan.com?a=1&b'
    url_query_value_blank_one_equals_mark = 'http://www.meituan.com?a=1&b='
    target_res = ['a', '1', 'b', '']
    assert utils.get_query_array(url_query_value_blank_no_equals_mark) == target_res
    assert utils.get_query_array(url_query_value_blank_one_equals_mark) == target_res
