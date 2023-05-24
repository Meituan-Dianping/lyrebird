import uuid
from lyrebird.log import get_logger


logger = get_logger()


def upgrade(self):
    MockData_2_13_0_to_2_14_0.upgrade(self)


class MockData_2_13_0_to_2_14_0:

    @staticmethod
    def upgrade(self):
        # mock data version 2.13.0 to 2.14.0
        root_id = self.context.root['id']
        root_children = self.context.root.get('children', [])
        for node in root_children:
            if node['type'] == 'config':
                return
        logger.warning('Upgrade mock data from 2.13.0 to 2.14.0 start')

        config_node_id = str(uuid.uuid4())
        new_node = {
            'id': config_node_id,
            'type': 'config',
            'parent_id': self.context.root['id'],
            'name': '.Settings'
        }

        # Save prop
        self.context.add_data(root_id, new_node)

        logger.warning('Upgrade mock data from 2.13.0 to 2.14.0 completed')
