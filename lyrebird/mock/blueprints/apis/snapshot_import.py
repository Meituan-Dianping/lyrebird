import uuid
from flask import redirect
from ....version import VERSION
from lyrebird import application
from flask_restful import Resource, request
from lyrebird.mock import context


class SanpshotImport(Resource):
    def get(self, url):
        application.snapshot_import_uri = url
        application.active_menu = {
            'name': 'datamanager',
            'title': 'DataManager',
            'type': 'router',
            'path': '/datamanager'
        }
        return redirect(f"/ui/?v={VERSION}#/datamanager/import")

    def post(self):
        if request.json:
            parent_id = request.json.get('parent_id')
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
                return application.make_fail_response(f'Unknown file type `.{path.suffix}``, `.lb` is required!')

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
