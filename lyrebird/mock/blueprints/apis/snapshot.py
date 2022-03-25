import uuid
import traceback
from pathlib import Path
from flask import redirect, send_file
from lyrebird import application
from lyrebird.version import VERSION
from flask_restful import Resource, request
from urllib.parse import urlencode
from lyrebird.mock import context
from lyrebird.log import get_logger


logger = get_logger()


class SnapshotImport(Resource):
    def get(self):
        queries = request.args
        new_query = {}
        application.active_menu = {
            'name': 'datamanager',
            'title': 'DataManager',
            'type': 'router',
            'path': '/datamanager'
        }

        group_id = queries.get('id')
        node = context.application.data_manager.id_map.get(group_id)
        if group_id and node:
            new_query['groupId'] = group_id

        elif queries.get('path'):
            if group_id:
                new_query['infoMsg'] = f'Snapshot {group_id} not found, use path argument instead'

            import_uri_link = queries['path']
            parent_path = queries.get('parent') or '/'
            parent_id = context.application.data_manager.add_group_by_path(parent_path)

            # is advanced save
            if queries.get('isAdvancedSave') == 'true':
                import_uri_uuid = str(uuid.uuid4())
                new_query['snapshotId'] = import_uri_uuid
                context.application.data_manager.snapshot_import_cache[import_uri_uuid] = {'link': import_uri_link}
                return redirect(f'/ui/?v={VERSION}#/datamanager/import?{urlencode(new_query)}')

            path = context.application.data_manager.read_snapshot_from_link(import_uri_link)

            try:
                group_id = context.application.data_manager.import_from_file(parent_id, path)
                new_query['groupId'] = group_id
            except Exception:
                new_query['errorMsg'] = f'Import snapshot error!'
                logger.error(f'Import snapshot error!\n {traceback.format_exc()}')
                return redirect(f'/ui/?v={VERSION}#/datamanager?{urlencode(new_query)}')

        if queries.get('isAutoActive') == 'true':
            context.application.data_manager.activate(group_id)

        display_info = queries.get('displayKey', '')
        if display_info:
            new_query['displayKey'] = display_info

        return redirect(f'/ui/?v={VERSION}#/datamanager?{urlencode(new_query)}')

    def post(self):
        if request.files:
            stream = request.files['file']
            if not stream:
                return application.make_fail_response('Missing required file')

            parent_id = request.form.get('parent_id') if request.form else None
            if not parent_id:
                return application.make_fail_response('Missing required argument: parent_id')

            filename = stream.filename or str(uuid.uuid4())
            path = context.application.data_manager.snapshot_workspace / filename
            stream.save(str(path))

            group_id = context.application.data_manager.import_from_file(parent_id, path)
            return application.make_ok_response(group_id=group_id)

        elif request.json:
            parent_id = request.json.get('parentId')
            name = request.json.get('snapshotName', '')
            if not parent_id:
                return application.make_fail_response('Missing required argument: parent_id')

            snapshot_id = request.json.get('snapshotId')
            snapshot_info = context.application.data_manager.snapshot_import_cache.get(snapshot_id)
            if not snapshot_info:
                return application.make_fail_response(f'Snapshot cache {snapshot_id} not found!')

            path = snapshot_info.get('path')
            if not Path(path).exists():
                link = snapshot_info.get('link')
                path = context.application.data_manager.read_snapshot_from_link(link)
                context.application.data_manager.snapshot_import_cache[snapshot_id]['path'] = path

            group_id = context.application.data_manager.import_from_file(parent_id, path, name=name)
            return application.make_ok_response(group_id=group_id)

        return application.make_fail_response('No import snapshot info found!')

    def put(self):
        if request.json:
            group_id = context.application.data_manager.import_from_local(request.json)
            return application.make_ok_response(group_id=group_id)

class SnapshotExport(Resource):
    def get(self, group_id):
        file = context.application.data_manager.export_from_remote(group_id)
        return send_file(file)

    def post(self):
        if not request.json.get('snapshot'):
            return application.make_fail_response('Missing required argument: snapshot')

        if not request.json.get('events'):
            return application.make_fail_response('Missing required argument: events')

        group_id, file_ = context.application.data_manager.export_from_local(request.json)
        req = send_file(file_)
        req.headers.add('SnapshotId', group_id)
        return req


class Snapshot(Resource):
    def get(self, snapshot_id):
        link = context.application.data_manager.snapshot_import_cache.get(snapshot_id, {}).get('link')
        if not link:
            application.make_fail_response(f'No import snapshot {snapshot_id} link found!')
        path = context.application.data_manager.read_snapshot_from_link(link)
        context.application.data_manager.snapshot_import_cache[snapshot_id]['path'] = path
        detail, output_path = context.application.data_manager.get_snapshot_file_detail(path)

        context.application.data_manager._remove_file([output_path])

        detail.pop('children')
        return application.make_ok_response(data=detail)
