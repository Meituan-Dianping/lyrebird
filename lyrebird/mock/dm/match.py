from jsonschema import validate
from lyrebird import utils
from lyrebird.mock.dm.jsonpath import jsonpath


class MatchRules:
    MATCH_SCHEMA = {
        "type": "object",
        "patternProperties": {
            ".": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "number"},
                    {"type": "boolean"},
                    {"type": "null"},
                ]
            }
        }
    }

    EXISTS_SCHEMA = {
        "type": "array",
        "items": {
            "type": "string"
        }
    }

    BOOL_SCHEMA = {
        "type": "object",
        "properties": {
            "match": MATCH_SCHEMA,
            "exists": EXISTS_SCHEMA
        },
        "additionalProperties": False
    }

    RULES_V2_SCHEMA = {
        "type": "object",
        "properties": {
            "must": BOOL_SCHEMA,
            "must_not": BOOL_SCHEMA,
        },
        "additionalProperties": False
    }

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

        if MatchRules.is_rule_v2(rules):
            return MatchRules._is_match_rule_v2(flow, rules)

        elif MatchRules.is_rule_v1(rules):
            return MatchRules._is_match_rule_v1(flow, rules)

        return False

    @staticmethod
    def is_rule_v1(rules):
        try:
            validate(instance=rules, schema=MatchRules.MATCH_SCHEMA)
            return True
        except Exception:
            return False

    @staticmethod
    def is_rule_v2(rules):
        try:
            validate(instance=rules, schema=MatchRules.RULES_V2_SCHEMA)
            return True
        except Exception:
            return False

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
