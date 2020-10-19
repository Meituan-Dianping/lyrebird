import re
import traceback
from lyrebird.log import get_logger

logger = get_logger()


class FunctionExecutor:

    @staticmethod
    def _func_handler(func_list, flow, handler_name='flow_editor'):
        for func_info in func_list:
            handler_fn = func_info['func']
            try:
                handler_fn(flow)
                # TODO: The flow is changed or not?
                action = {
                    'id': handler_name,
                    'name': func_info['name']
                }
                if flow.get('action'):
                    flow['action'].append(action)
                else:
                    flow['action'] = [action]
            except Exception:
                logger.error(traceback.format_exc())

    @classmethod
    def _get_matched_handler(cls, func_list, flow):
        matched_func = []
        for func in func_list:
            rules = func['rules']
            if not rules or cls._is_req_match_rule(rules, flow):
                matched_func.append(func)
        return matched_func

    @classmethod
    def _is_req_match_rule(cls, rules, flow):
        for rule_key in rules:
            pattern = rules[rule_key]
            target = cls._get_rule_target(rule_key, flow)
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
