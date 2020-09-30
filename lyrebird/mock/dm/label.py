import hashlib
from lyrebird.mock import context


class LabelHandler:

    def __init__(self):
        self.label_map = {}
        self.isolated_label_ids = set()
        self.default_color = '#808695'
        self.default_description = ''

    def get_label(self, node):
        # collect isolated label
        self.isolated_label_ids = set()
        isolated_labels = {}
        for label_id, label in self.label_map.items():
            if not label['groups']:
                self.isolated_label_ids.add(label_id)
                isolated_labels[label_id] = label

        # init label_map
        self.label_map = {}
        self._collect_label(node)

        # add isolated_label
        for key in self.label_map:
            if key in isolated_labels:
                isolated_labels.pop(key)
        self.label_map.update(isolated_labels)

    def _make_label_info(self, group):
        group_id = group['id']
        label_list = group.get('label')
        if not isinstance(label_list, list):
            return

        for label in label_list:
            name = label.get('name')
            if not name:
                continue
            label_id = self._get_label_name_md5(label)
            if self.label_map.get(label_id):
                self.label_map[label_id]['groups'].append(group_id)
            else:
                self.label_map[label_id] = {
                    'id': label_id,
                    'name': label['name'],
                    'color': label.get('color') or self.default_color,
                    'description': label.get('description') or '',
                    'groups': [group_id]
                }

    def _collect_label(self, node):
        if node['type'] == 'group' and 'label' in node:
            self._make_label_info(node)
        if 'children' in node:
            for child in node['children']:
                self._collect_label(child)

    def create_label(self, label):
        label_name = label.get('name')
        if not label_name:
            raise LabelNameNotFound

        label_id = self._get_label_name_md5(label)
        new_label = {
            label_id: {
                'id': label_id,
                'name': label['name'],
                'color': label.get('color') or self.default_color,
                'description': label.get('description') or '',
                'groups': []
            }
        }
        self.isolated_label_ids.add(label_id)
        self.label_map.update(new_label)

    def update_label(self, update_label):
        target_label_id = update_label['id']
        update_name = update_label.get('name')
        update_color = update_label.get('color') or self.default_color
        update_description = update_label.get('description') or self.default_description
        if not update_name:
            raise LabelNameNotFound

        target_label = self.label_map.get(target_label_id)
        groups = target_label.get('groups') or []
        for group_id in groups:
            _group = context.application.data_manager.id_map.get(group_id)
            label_list = _group.get('label')
            if not isinstance(label_list, list):
                raise LabelTypeIsNotList(f'Unexpected label value type: {type(label_list)}')

            for label in label_list:
                label_id = self._get_label_name_md5(label)
                if label_id != target_label_id:
                    continue
                label['name'] = update_name
                label['color'] = update_color
                label['description'] = update_description
                break

            context.application.data_manager.update_group(group_id, _group, save=False)

        if groups:
            context.application.data_manager._save_prop()
            context.application.data_manager.reload()

        # update label_map
        self.label_map[target_label_id]['name'] = update_name
        self.label_map[target_label_id]['color'] = update_color
        self.label_map[target_label_id]['description'] = update_description

        # update label_map id if label_id is changed
        new_label_id = self._get_label_name_md5(update_label)
        if new_label_id != target_label_id:
            self.label_map[target_label_id]['id'] = new_label_id
            self.label_map[new_label_id] = self.label_map[target_label_id]
            self.label_map.pop(target_label_id)

    def delete_label(self, target_label_id):
        target_label = self.label_map.get(target_label_id)
        groups = target_label.get('groups') or []
        for group_id in groups:
            _group = context.application.data_manager.id_map.get(group_id)
            label_list = _group.get('label')
            if not isinstance(label_list, list):
                raise LabelTypeIsNotList(f'Unexpected label value type: {type(label_list)}')

            for label in label_list[::-1]:
                label_id = self._get_label_name_md5(label)
                if label_id != target_label_id:
                    continue
                label_list.remove(label)
                break

            context.application.data_manager.update_group(group_id, _group, save=False)

        if groups:
            context.application.data_manager._save_prop()
            context.application.data_manager.reload()

        # update data_map
        self.label_map.pop(target_label_id)
        if target_label_id in self.isolated_label_ids:
            self.isolated_label_ids.remove(target_label_id)

    def _get_label_name_md5(self, label):
        keyword = label['name']
        md5_module = hashlib.sha224()
        md5_module.update(bytes(keyword, encoding="utf-8"))
        return md5_module.hexdigest()


class LabelNotFound(Exception):
    pass


class LabelTypeIsNotList(Exception):
    pass


class LabelNameNotFound(Exception):
    pass
