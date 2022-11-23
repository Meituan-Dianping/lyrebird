from lyrebird.mock.dm import MatchRules


# ------------ rule v1 ------------

def test_match_is_rule_v1_string():
    rule = {
        'request.url': 'path'
    }
    res = MatchRules.is_rule_v1(rule)
    assert res == True


def test_match_is_rule_v1_number_int():
    rule = {
        'request.data.id': 1
    }
    res = MatchRules.is_rule_v1(rule)
    assert res == True


def test_match_is_rule_v1_number_float():
    rule = {
        'request.data.price': 2.5
    }
    res = MatchRules.is_rule_v1(rule)
    assert res == True


def test_match_is_rule_v1_bool():
    rule = {
        'request.data.isOpen': True
    }
    res = MatchRules.is_rule_v1(rule)
    assert res == True


def test_match_is_rule_v1_null():
    rule = {
        'request.data': None
    }
    res = MatchRules.is_rule_v1(rule)
    assert res == True


def test_match_is_rule_v1_rule_unexpected_type():
    rule_list = []
    res = MatchRules.is_rule_v1(rule_list)
    assert res == False

    rule_none = None
    res = MatchRules.is_rule_v1(rule_none)
    assert res == False


def test_match_is_rule_v1_value_unexpected_type():
    rule_value_dict = {
        'request.data': {}
    }
    res = MatchRules.is_rule_v1(rule_value_dict)
    assert res == False

    rule_value_list = {
        'request.data': []
    }
    res = MatchRules.is_rule_v1(rule_value_list)
    assert res == False


# ------------ rule v2 ------------


def test_match_is_rule_v2_rule_unexpected_type():
    rule_list = []
    res = MatchRules.is_rule_v2(rule_list)
    assert res == False

    rule_none = None
    res = MatchRules.is_rule_v2(rule_none)
    assert res == False


def test_match_is_rule_v2_rule_unexpected_bool_key():
    rule_not_exists_bool_key = {
        'not_exists_bool_key': {}
    }
    res = MatchRules.is_rule_v2(rule_not_exists_bool_key)
    assert res == False


def test_match_is_rule_v2_rule_unexpected_query_key():
    rule_not_exists_query_key = {
        'must': {
            'not_exists_query_key': {}
        }
    }
    res = MatchRules.is_rule_v1(rule_not_exists_query_key)
    assert res == False


def test_match_is_rule_v2_must_match_string():
    rule = {
        'must': {
            'match': {
                'request.url': 'path'
            }
        }
    }
    res = MatchRules.is_rule_v2(rule)
    assert res == True


def test_match_is_rule_v2_must_match_number_int():
    rule = {
        'must': {
            'match': {
                'request.data.id': 1
            }
        }
    }
    res = MatchRules.is_rule_v2(rule)
    assert res == True


def test_match_is_rule_v2_must_match_number_float():
    rule = {
        'must': {
            'match': {
                'request.data.price': 2.5
            }
        }
    }
    res = MatchRules.is_rule_v2(rule)
    assert res == True


def test_match_is_rule_v2_must_match_bool():
    rule = {
        'must': {
            'match': {
                'request.data.isOpen': True
            }
        }
    }
    res = MatchRules.is_rule_v2(rule)
    assert res == True


def test_match_is_rule_v2_must_match_null():
    rule = {
        'must': {
            'match': {
                'request.data': None
            }
        }
    }
    res = MatchRules.is_rule_v2(rule)
    assert res == True


def test_match_is_rule_v2_must_exists():
    rule = {
        'must': {
            'exists': ['request.data.id']
        }
    }
    res = MatchRules.is_rule_v2(rule)
    assert res == True


def test_match_is_rule_v2_must_not_match_string():
    rule = {
        'must_not': {
            'match': {
                'request.url': 'path'
            },
            'exists': ['request.data.id']
        }
    }
    res = MatchRules.is_rule_v2(rule)
    assert res == True


# ------------ jsonpath ------------


def test_match_jsonpath_simple():
    flow = {
        'request': {
            'url': 'http://somehost/api/search'
        }
    }

    rule = {
        'request.url': '/api/search'
    }
    res = MatchRules._is_match_rule_v1(flow, rule)
    assert res == True

    rule = {
        'request.url': '/api/location'
    }
    res = MatchRules._is_match_rule_v1(flow, rule)
    assert res == False


def test_match_jsonpath_array():
    rule = {
        'request.data.poi[*].name': '(?=.*app)',
        'request.url': '(?=.*search)'
    }

    flowA = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'poi':[
                    {'name':'app'},
                    {'name':'apple'}
                ]
            }
        }
    }
    res = MatchRules._is_match_rule_v1(flowA, rule)
    assert res == True

    flowB = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'poi':[
                    {'name':'app'},
                    {'name':'banana'}
                ]
            }
        }
    }
    res = MatchRules._is_match_rule_v1(flowB, rule)
    assert res == False


# ------------ match  ------------


def test_match_v1():
    rule = {
        'request.url': '(?=.*search)'
    }

    flow = {
        'request': {
            'url': 'http://somehost/api/search'
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == True

    flow = {
        'request': {
            'url': 'http://somehost/api/location'
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False


def test_match_v2_must_exists():
    rule = {
        'must': {
            'exists': ['request.url']
        }
    }

    flow = {
        'request': {
            'url': 'http://somehost/api/search'
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == True

    flow = {
        'request': {
            'data': 'a'
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False


def test_match_v2_must_not_exists():
    rule = {
        'must_not': {
            'exists': ['request.data']
        }
    }

    flow = {
        'request': {
            'url': 'http://somehost/api/search'
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == True

    flow = {
        'request': {
            'data': 'a'
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False


def test_match_v2_must_match_string():
    rule = {
        'must': {
            'match': {
                'request.url': '/api/search'
            }
        }
    }

    flow = {
        'request': {
            'url': 'http://somehost/api/search'
        }
    }

    res = MatchRules.match(flow, rule)
    assert res == True


def test_match_v2_must_match_string():
    rule = {
        'must': {
            'match': {
                'request.url': '/api/search'
            }
        }
    }

    flow_a = {
        'request': {
            'url': 'http://somehost/api/search'
        }
    }
    res = MatchRules.match(flow_a, rule)
    assert res == True

    flow_b = {
        'request': {
            'url': 'http://somehost/api/location'
        }
    }
    res = MatchRules.match(flow_b, rule)
    assert res == False


def test_match_v2_must_match_number():
    rule = {
        'must': {
            'match': {
                'request.data.sort': 1,
                'request.url': '(?=.*search)'
            }
        }
    }

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': 1
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == True

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': 1.0
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': 222
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': '1'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False


def test_match_v2_must_match_bool():
    rule = {
        'request.data.sort': True,
        'request.url': '(?=.*search)'
    }

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': True
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == True

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': False
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': 'True'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False


def test_mock_rule_null_with_jsonpath():
    rule = {
        'request.data.sort': None,
        'request.url': '(?=.*search)'
    }

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': None
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == True

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': ''
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'sort': 'None'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False


def test_match_v2_must_not_match_string():
    rule = {
        'must_not': {
            'match': {
                'request.data.name': '(?=.*a)',
                'request.url': '(?=.*search)'
            }
        }
    }

    flow = {
        'request': {
            'url': 'http://somehost/api/location',
            'data': {
                'name': 'b'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == True

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'name': 'a'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'name': 'b'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False

    flow = {
        'request': {
            'url': 'http://somehost/api/location',
            'data': {
                'name': 'a'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False


def test_match_v2_must_and_must_not_match_string():
    rule = {
        'must': {
            'match': {
                'request.url': '(?=.*search)'
            }
        },
        'must_not': {
            'match': {
                'request.data.name': '(?=.*a)',
            }
        }
    }

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'name': 'b'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == True

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'name': 'a'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False

    flow = {
        'request': {
            'url': 'http://somehost/api/location',
            'data': {
                'name': 'b'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'name': 'a'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == False


def test_match_v2_all():
    rule = {
        'must': {
            'match': {
                'request.url': '(?=.*search)',
                'request.data.must_match_key': '(?=.*must_match_value)',
            },
            'exists': ['request.data.must_exists_key']
        },
        'must_not': {
            'match': {
                'request.data.must_not_match_key': '(?=.*must_not_match_value)'
            },
            'exists': ['request.data.must_not_exists_key']
        }
    }

    flow = {
        'request': {
            'url': 'http://somehost/api/search',
            'data': {
                'must_match_key': 'must_match_value',
                'must_exists_key': 'empty',
                'must_not_match_key': 'empty'
            }
        }
    }
    res = MatchRules.match(flow, rule)
    assert res == True
