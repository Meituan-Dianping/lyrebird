from lyrebird import utils

def test_case_insenstive_dict():
    test_dict = utils.CaseInsensitiveDict({'Content-Type':'LBTests'})
    assert test_dict.get('Content-Type') == 'LBTests'
    assert test_dict.get('content-type') == 'LBTests'
    test_dict = utils.CaseInsensitiveDict({'content-type':'LBTests'})
    assert test_dict.get('Content-Type') == 'LBTests'
    assert test_dict.get('content-type') == 'LBTests'


# def get_query_array(url):
#     # query string to array, example:
#     # a=1&b=2 ==> ['a', '1', 'b', '2']
#     # a=&b=2 ==> ['a', '', 'b', '2']
#     # a&b=2 ==> ['a', '', 'b', '2']
#     query_array = []
#     qs_index = url.find('?')
#     if qs_index < 0:
#         return query_array

#     query_string = url[qs_index+1:]
#     for k_v in query_string.split('&'):
#         k_v_item = k_v.split('=')
#         if len(k_v_item) >= 2:
#             query_array.extend(k_v_item[:2])
#         else:
#             query_array.extend([k_v, ''])
#     return query_array


def test_get_query_array():
    url_no_query = 'http://www.meituan.com'
    url_no_query_with_question_mark = 'http://www.meituan.com?'
    target_res = []
    assert utils.get_query_array(url_no_query) == target_res
    assert utils.get_query_array(url_no_query_with_question_mark) == target_res

    url_query_normal = f'http://www.meituan.com?a=1&b=2'
    url_query_value_blank_multiple_equals_mark = f'http://www.meituan.com?a=1&b=2=3'
    target_res = ['a', '1', 'b', '2']
    assert utils.get_query_array(url_query_normal) == target_res
    assert utils.get_query_array(url_query_value_blank_multiple_equals_mark) == target_res

    url_query_value_blank_no_equals_mark = f'http://www.meituan.com?a=1&b'
    url_query_value_blank_one_equals_mark = f'http://www.meituan.com?a=1&b='
    target_res = ['a', '1', 'b', '']
    assert utils.get_query_array(url_query_value_blank_no_equals_mark) == target_res
    assert utils.get_query_array(url_query_value_blank_one_equals_mark) == target_res
