import re
from lyrebird.log import get_logger


logger = get_logger()


class MockRouter:
    def __init__(self):
        self.data_map = []
        self.parent_data_map = []

    def switch_group(self, data_group, parent=None):
        self.data_map = []
        self.parent_data_map = []
        if not data_group:
            return
        for data_id in data_group.all_data:
            data = data_group.all_data[data_id]
            self.data_map.append((MockRule(data.rule), data))
        if parent:
            for data_id in parent.all_data:
                data = parent.all_data[data_id]
                self.parent_data_map.append((MockRule(data.rule), data))

    def get_mock_data(self, flow):
        for rule, data in self.data_map:
            if rule.match(flow):
                logger.debug(f'Found mock data by rule {rule}')
                return data
        for rule, data in self.parent_data_map:
            if rule.match(flow):
                logger.debug(f'Found mock data by rule {rule} from parent')
                return data
        # TODO none return

class MockRule:
    def __init__(self, rule):
        self.rule = rule

    def match(self, flow):
        if not self.rule:
            return False
        for rule_name in self.rule:
            pattern = self.rule[rule_name]
            target = self._get_target_content(rule_name, flow)
            if not re.search(pattern, target):
                return False
        return True

    def _get_target_content(self, rule_name, flow):
        prop_keys = rule_name.split('.')
        result = flow
        for prop_key in prop_keys:
            result = result.get(prop_key)
            if not result:
                return None
        return result

    def __str__(self):
        return f'MockRule: {self.rule}'
