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

        context.application.data_manager.import_snapshot(parent_id, name)
        return application.make_ok_response()


class SnapShotImportDetail(Resource):
    def get(self):
        snapshot_detail = context.application.data_manager.decompress_snapshot()['snapshot_detail']
        snapshot_detail.pop('children')
        return application.make_ok_response(data=snapshot_detail)
