import uuid
import requests
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
                context.application.data_manager.snapshot_import_uri_map[import_uri_uuid] = import_uri_link
                return redirect(f'http://localhost:8080/ui/?v={VERSION}#/datamanager/import?{urlencode(new_query)}')

            path = context.application.data_manager.read_snapshot_from_link(import_uri_link)

            try:
                group_id = context.application.data_manager.import_from_file(parent_id, path)
                new_query['groupId'] = group_id
            except Exception:
                new_query['errorMsg'] = f'Import snapshot error!'
                logger.error(f'Import snapshot error!\n {traceback.format_exc()}')
                return redirect(f'http://localhost:8080/ui/?v={VERSION}#/datamanager?{urlencode(new_query)}')

        if queries.get('isAutoActive') == 'true':
            context.application.data_manager.deactivate()
            context.application.data_manager.activate(group_id)

        display_info = queries.get('displayKey', '')
        if display_info:
            new_query['displayKey'] = display_info

        return redirect(f'http://localhost:8080/ui/?v={VERSION}#/datamanager?{urlencode(new_query)}')

    def post(self):
        if request.json:
            group_id = context.application.data_manager.import_from_local(request.json)

        elif request.files:
            stream = request.files['file']
            if not stream:
                return application.make_fail_response('Missing required file')

            parent_id = request.form.get('parent_id') if request.form else None
            if not parent_id:
                return application.make_fail_response('Missing required argument: parent_id')

            filename = stream.filename or str(uuid.uuid4())
            path = application._cm.ROOT / 'snapshot' / filename
            stream.save(str(path))

            group_id = context.application.data_manager.import_from_file(parent_id, path)

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
        link = context.application.data_manager.snapshot_import_uri_map.get(snapshot_id)
        path = context.application.data_manager.read_snapshot_from_link(link)
        detail, output_path = context.application.data_manager._get_snapshot_file_detail(path)

        tmp_snapshot_file_list = [path, output_path]
        context.application.data_manager._remove_file(tmp_snapshot_file_list)

        detail.pop('children')
        return application.make_ok_response(data=detail)
