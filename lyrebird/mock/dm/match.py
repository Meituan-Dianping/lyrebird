from lyrebird import utils
from lyrebird.mock.dm.jsonpath import jsonpath


class MatchRules:
    def validate_match(rules):
        '''
        { 'request.url': 'pathA/pathB' }

        Empty is allowed
        '''
        if not isinstance(rules, dict):
            return False
        for value in rules.values():
            if not (isinstance(value, (str, int, float, bool)) or value is None):
                return False
        return True

    BOOL_KEY = set(['must', 'must_not'])

    def validate_exists(rules):
        '''
        [ "request.url", "request.data.name" ]

        Empty is allowed
        '''
        if not isinstance(rules, list):
            return False
        for value in rules:
            if not isinstance(value, str):
                return False
        return True

    def validate_query(rules):
        '''
        {
            "match": { ... },
            "exists": [ ... ]
        }

        Empty is allowed
        '''
        if not isinstance(rules, dict):
            return False
        if set(rules.keys()) - set(MatchRules.QUERY_FUNC_MAP.keys()):
            return False

        for query_key, query_rule in rules.items():
            if query_key == 'match':
                if not MatchRules.validate_match(query_rule):
                    return False
            elif query_key == 'exists':
                if not MatchRules.validate_exists(query_rule):
                    return False
        return True

    def validate_bool(rules):
        '''
        {
            "must": { ... },
            "must_not": { ... }
        }
        '''
        if not isinstance(rules, dict):
            return False
        if set(rules.keys()) - set(MatchRules.BOOL_FUNC_MAP.keys()):
            return False

        for search in rules.values():
            if not MatchRules.validate_query(search):
                return False

        return True

    @staticmethod
    def match(flow, rules):
        '''
        1. simple rule
        simple rule is `must.match` in complex rule
        {
            'request.url': 'path/path'
        }

        2. complex rule
        {
            "must": {
                "match": {
                    'request.url': 'path/path'
                }
            },
            "must_not": {
                "match": {
                    "request.url": 'isUpdate'
                },
                "exists": [
                    "request.url"
                ]
            }
        }
        '''

        if not rules:
            return False

        if not isinstance(rules, dict):
            return False

        if MatchRules.is_rule_v1(rules):
            return MatchRules._is_match_rule_v1(flow, rules)

        if MatchRules.is_rule_v2(rules):
            return MatchRules._is_match_rule_v2(flow, rules)

        return False

    @staticmethod
    def is_rule_v1(rules):
        return MatchRules.validate_match(rules)

    @staticmethod
    def is_rule_v2(rules):
        return MatchRules.validate_bool(rules)

    @staticmethod
    def _is_match_rule_v1(flow, rules):
        return MatchRules._query_match(flow, rules)

    @staticmethod
    def _is_match_rule_v2(flow, rules:dict):
        for bool_key, bool_value in rules.items():
            if not bool_value:
                return False
            if bool_key not in MatchRules.BOOL_FUNC_MAP:
                return False
            if not MatchRules.BOOL_FUNC_MAP[bool_key](flow, bool_value):
                return False

        return True

    @staticmethod
    def _bool_must(flow, query:dict, expected=True):
        '''
        query = {
            "match": {
                'request.url': 'path/path'
            }
        }
        '''
        for query_key, query_value in query.items():
            if not query_value:
                return False
            if query_key not in MatchRules.QUERY_FUNC_MAP:
                return False
            if not MatchRules.QUERY_FUNC_MAP[query_key](flow, query_value, expected=expected):
                return False

        return True

    @staticmethod
    def _bool_must_not(flow, query:dict):
        '''
        query = {
            "match": {
                'request.url': 'path/path'
            }
        }
        '''
        return MatchRules._bool_must(flow, query, expected=False)

    @staticmethod
    def _query_exists(flow, exists:dict, expected=True):
        '''
        exists = [
            'request.data'
        ]
        '''
        for exists_key in exists:
            search_res = jsonpath.search(flow, exists_key)
            if bool(search_res) != expected:
                return False
        return True

    @staticmethod
    def _query_match(flow, match:dict, expected=True):
        '''
        match = {
            'request.url': 'path/path'
        }
        '''
        for match_key, match_pattern in match.items():
            targets = MatchRules._get_targets(flow, match_key)
            if targets == []:
                return False
            if not MatchRules._is_targets_pattern_matched(match_pattern, targets, expected=expected):
                return False
        return True

    @staticmethod
    def _get_targets(flow, key):
        search_res = jsonpath.search(flow, key)
        if not search_res:
            return []
        return [s.node for s in search_res]

    @staticmethod
    def _is_targets_pattern_matched(pattern, targets, expected=True):
        for target in targets:
            if utils.TargetMatch.is_match(target, pattern) != expected:
                return False
        return True


    BOOL_FUNC_MAP = {
        'must': _bool_must.__func__,
        'must_not': _bool_must_not.__func__,
    }

    QUERY_FUNC_MAP = {
        'match': _query_match.__func__,
        'exists': _query_exists.__func__
    }
