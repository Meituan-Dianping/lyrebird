import uuid
import traceback
from flask import redirect
from lyrebird import application
from lyrebird.version import VERSION
from flask_restful import Resource, request
from urllib.parse import urlencode
from lyrebird.mock import context
from lyrebird.log import get_logger


logger = get_logger()


class SanpshotImport(Resource):
    def get(self):
        queries = request.args
        url = queries.get('path')
        application.snapshot_import_uri = url
        application.active_menu = {
            'name': 'datamanager',
            'title': 'DataManager',
            'type': 'router',
            'path': '/datamanager'
        }
        if not url:
            return redirect(f"/ui/?v={VERSION}#/datamanager/import")

        # is advanced save
        if queries.get('isAdvancedSave') == 'true':
            return redirect(f"/ui/?v={VERSION}#/datamanager/import")

        # auto import into parent
        info = context.application.data_manager.decompress_snapshot()
        tmp_snapshot_file_list = [
            info['snapshot_storage_path'],
            f'{info["snapshot_storage_path"]}.lb'
        ]
        context.application.data_manager.remove_tmp_snapshot_file(tmp_snapshot_file_list)
        group_name = info['snapshot_detail']['name']

        parent_path = queries.get('parent') or '/'
        parent_id = context.application.data_manager.add_group_by_path(parent_path)

        new_query = {}
        try:
            group_id = context.application.data_manager.import_snapshot(parent_id, group_name)
            new_query['groupId'] = group_id
        except Exception:
            new_query['errorMsg'] = f'Import snapshot error: Snapshot {group_name} is broken!'
            new_query_str = urlencode(new_query)
            logger.error(f'Import snapshot error!\n {traceback.format_exc()}')
            return redirect(f"http://localhost:9090/ui/?v={VERSION}#/datamanager?{new_query_str}")

        # auto active
        if queries.get('isAutoActive') == 'true':
            context.application.data_manager.deactivate()
            context.application.data_manager.activate(group_id)

        display_info = queries.get('displayKey', '')
        if display_info:
            new_query['displayKey'] = display_info

        new_query_str = urlencode(new_query)
        return redirect(f"/ui/?v={VERSION}#/datamanager?{new_query_str}")

    def post(self):
        if request.json:
            parent_id = request.json.get('parentId')
            name = request.json.get('snapshotName', '')
            if not parent_id:
                return application.make_fail_response('parent_id is required!')

            context.application.data_manager.import_snapshot(parent_id, name)

        elif request.files:
            parent_id = request.form.get('parent_id') if request.form else ''
            if not parent_id:
                return application.make_fail_response('parent_id is required!')

            stream = request.files['file']
            if not stream:
                return application.make_fail_response('file is required!')

            filename = stream.filename or str(uuid.uuid4())
            path = application._cm.ROOT / 'snapshot' / filename
            if path.suffix != '.lb':
                return application.make_fail_response(f'Unknown file type `.{path.suffix}`, `.lb` is required!')

            stream.save(str(path))
            application.snapshot_import_uri = f'file://{str(path)}'
            name = path.stem

            context.application.data_manager.import_snapshot(parent_id, name, path=path)

        return application.make_ok_response()


class SnapShotImportDetail(Resource):
    def get(self):
        info = context.application.data_manager.decompress_snapshot()
        tmp_snapshot_file_list = [
            info['snapshot_storage_path'],
            f'{info["snapshot_storage_path"]}.lb'
        ]
        context.application.data_manager.remove_tmp_snapshot_file(tmp_snapshot_file_list)

        detail = info['snapshot_detail']
        detail.pop('children')
        return application.make_ok_response(data=detail)
