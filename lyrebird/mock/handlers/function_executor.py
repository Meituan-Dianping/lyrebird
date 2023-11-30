import re
import traceback
from lyrebird.log import get_logger
from lyrebird.utils import HookedDict

logger = get_logger()


class FunctionExecutor:

    @staticmethod
    def func_handler(func_list, flow, handler_type='flow_editor'):
        for func_info in func_list:
            handler_fn = func_info['func']
            try:
                handler_fn(flow)
                # TODO: The flow is changed or not?
                action = {
                    'id': handler_type,
                    'name': func_info['name']
                }
                if flow.get('action'):
                    flow['action'].append(action)
                else:
                    flow['action'] = [action]
            except Exception:
                logger.error(traceback.format_exc())

    @staticmethod
    def get_matched_sorted_handler(func_list, flow):
        matched_func = []
        if not isinstance(flow, HookedDict):
            flow = HookedDict(flow)
        for func in func_list:
            rules = func['rules']
            if not rules or FunctionExecutor._is_req_match_rule(rules, flow):
                matched_func.append(func)
        matched_sorted_func = sorted(matched_func, key = lambda f:f['rank'])
        return matched_sorted_func

    @staticmethod
    def _is_req_match_rule(rules, flow):
        for rule_key in rules:
            pattern = rules[rule_key]
            target = FunctionExecutor._get_rule_target(rule_key, flow)
            if not target or not re.search(pattern, target):
                return False
        return True

    @staticmethod
    def _get_rule_target(rule_key, flow):
        prop_keys = rule_key.split('.')
        result = flow
        for prop_key in prop_keys:
            result = result.get(prop_key)
            if not result:
                return None
        return result
