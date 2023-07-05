import uuid
from lyrebird.log import get_logger


logger = get_logger()


def upgrade(self):
    MockData_2_13_0_to_2_14_0.upgrade(self)


class MockData_2_13_0_to_2_14_0:

    @staticmethod
    def upgrade(self):
        root_id = self.context.root['id']

        for node in self.context.id_map.values():
            if node['type'] == 'config' and node['parent_id'] == root_id:
                return

        logger.warning('Upgrade mock data from 2.13.0 to 2.14.0 start')
        new_node = {
            'id': str(uuid.uuid4()),
            'type': 'config',
            'parent_id': root_id,
            'name': '.Settings'
        }
        self.context.add_data(root_id, new_node)
        logger.warning('Upgrade mock data from 2.13.0 to 2.14.0 completed')
