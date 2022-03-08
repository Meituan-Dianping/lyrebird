from lyrebird.log import get_logger
from lyrebird.mock.dm.jsonpath import jsonpath
from lyrebird.utils import TargetMatch

logger = get_logger()


class Filter:
    
    @staticmethod
    def is_target_match_patterns(pattern_list, target):
        if not pattern_list or not target:
            return False
        for pattern in pattern_list:
            if TargetMatch.is_match(target, pattern):
                return True
        return False
    
    @staticmethod
    def is_jsonpath_match_patterns(pattern_list, json_obj, target_rule):
        target_nodes = jsonpath.search(json_obj, target_rule)
        for node in target_nodes:
            is_match = Filter.is_target_match_patterns(pattern_list, node.node)
            if is_match:
                return True
        return False

    @staticmethod
    def is_flow_match_filter(filter_dict, flow):
        for target_rule, patterns in filter_dict.items():
            if type(patterns) != list:
                patterns = [patterns]
            if not Filter.is_jsonpath_match_patterns(patterns, flow, target_rule):
                return False
        return True
    
    @staticmethod
    def get_items_after_filtration(source_items, filter_obj):
        if not filter_obj:
            return source_items
        advanced_filter = filter_obj.get('advanced', None)
        if advanced_filter:
            must_filter = advanced_filter.get('must', {})
            must_not_filter = advanced_filter.get('must_not', {})
        else:
            must_filter = {}
            must_not_filter = {}
            ignore_host = filter_obj.get('ignore', [])
            if ignore_host:
                must_not_filter = {
                    'request.host': ignore_host
                }
        result_items = []
        for item in source_items:
            if must_not_filter and Filter.is_flow_match_filter(must_not_filter, item):
                continue
            if must_filter and (not Filter.is_flow_match_filter(must_filter, item)):
                continue
            result_items.append(item)
        return result_items
