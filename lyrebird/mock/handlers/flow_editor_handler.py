import re
import traceback
from lyrebird import application
from lyrebird.log import get_logger

logger = get_logger()


class FlowEditorHandler:

    def __init__(self):
        self.on_request = application.on_request
        self.on_response = application.on_response
        self.on_request_upstream = application.on_request_upstream
        self.on_response_upstream = application.on_response_upstream

    def on_request_handler(self, handler_context):
        matched_funcs = self._get_matched_handler(self.on_request, handler_context.flow)
        if not matched_funcs:
            return

        self._func_handler(matched_funcs, handler_context.flow['request'])
        handler_context.set_request_edited()
        handler_context.flow['request']['headers']['lyrebird_modified'] = 'modified'

    def on_request_upstream_handler(self, handler_context):
        matched_funcs = self._get_matched_handler(self.on_request_upstream, handler_context.flow)
        if not matched_funcs:
            return

        self._func_handler(matched_funcs, handler_context.flow['request'])
        handler_context.set_request_edited()
        handler_context.flow['request']['headers']['lyrebird_modified'] = 'modified'

    def on_response_upstream_handler(self, handler_context):
        matched_funcs = self._get_matched_handler(self.on_response_upstream, handler_context.flow)
        if not matched_funcs:
            return

        if not handler_context.flow['response'].get('data'):
            handler_context.update_response_data2flow()

        self._func_handler(matched_funcs, handler_context.flow['response'])
        handler_context.set_response_edited()
        handler_context.flow['response']['headers']['lyrebird_modified'] = 'modified'

    def on_response_handler(self, handler_context):
        matched_funcs = self._get_matched_handler(self.on_response, handler_context.flow)
        if not matched_funcs:
            return

        if not handler_context.flow['response'].get('data'):
            handler_context.update_response_data2flow()

        self._func_handler(matched_funcs, handler_context.flow['response'])
        handler_context.set_response_edited()
        handler_context.flow['response']['headers']['lyrebird_modified'] = 'modified'

    def _func_handler(self, func_list, data):
        for func_info in func_list:
            handler_fn = func_info['func']
            try:
                handler_fn(data)
            except Exception:
                logger.error(traceback.format_exc())

    def _get_matched_handler(self, func_list, flow):
        matched_func = []
        for func in func_list:
            rules = func['rules']
            if not rules or self._is_req_match_rule(rules, flow):
                matched_func.append(func)
        return matched_func

    def _is_req_match_rule(self, rules, flow):
        for rule_key in rules:
            pattern = rules[rule_key]
            target = self._get_rule_target(rule_key, flow)
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
