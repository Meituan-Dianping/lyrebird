from flask import Blueprint, request
from flask_restful import Api
from .common import Status, WorkMode, Manifest, DiffMode, Render
from .flow import Flow, FlowList
from .mock import MockData, MockGroup, ActivatedMockGroup, MockGroupByName, MockDataLabel, TreeView, OpenNodes
from .config import Conf
from .menu import Menu
from .notice import Notice
from .checker import Checker
from .event import Event, EventExport, Channel, EventFileInfo
from .conflict_check import ConflictCheck, ActivatedDataConflictCheck
from .mock_editor import Cut, Copy, Paste, Duplicate
from .qrcode import Qrcode
from .search import SearchMockData
from .bandwidth import Bandwidth, BandwidthTemplates
from .status_bar import StatusBar
from .snapshot import SnapshotImport, SnapshotExport, Snapshot
from lyrebird.log import get_logger
from lyrebird import application


logger = get_logger()


api = Blueprint('api', __name__, url_prefix='/api')
api_source = Api(api, errors=Exception)


@api.after_request
def after_request(response):
    """
    输出每条请求概要信息
    """
    lyrebird_info = response.headers.get('lyrebird', default='')
    logger.info(f'[On API]{response.status_code} {lyrebird_info} {request.method} {request.url[:100]}')
    return response


api_source.add_resource(Status, '/status')
api_source.add_resource(Manifest, '/manifest')
api_source.add_resource(Flow, '/flow/<string:id>')
api_source.add_resource(FlowList, '/flow', '/flow/<string:action>')
api_source.add_resource(Cut, '/cut/<string:_id>')
api_source.add_resource(Copy, '/copy/<string:_id>')
api_source.add_resource(Paste, '/paste/<string:_id>')
api_source.add_resource(Duplicate, '/duplicate/<string:_id>')
api_source.add_resource(TreeView, '/tree')
api_source.add_resource(OpenNodes, '/tree/open-nodes')
api_source.add_resource(MockGroup, '/group', '/group/<string:group_id>', '/group/label/<string:label>')
api_source.add_resource(MockData, '/data', '/data/<string:_id>')
api_source.add_resource(SearchMockData, '/search/group', '/search/group/', '/search/group/name/', '/search/group/name/<string:search_str>')
api_source.add_resource(ConflictCheck, '/conflict/id/<string:group_id>')
api_source.add_resource(ActivatedDataConflictCheck, '/conflict/activated')
api_source.add_resource(ActivatedMockGroup, '/mock/activated', '/mock/activated/flow','/mock/<string:group_id>/<string:action>')
api_source.add_resource(MockGroupByName, '/mock_by_name')
api_source.add_resource(MockDataLabel, '/label')
api_source.add_resource(Qrcode, '/qrcode')
api_source.add_resource(Conf, '/conf')
api_source.add_resource(WorkMode, '/mode', '/mode/<string:mode>')
api_source.add_resource(DiffMode, '/diffmode')
api_source.add_resource(Render, '/render')
api_source.add_resource(Menu, '/menu')
api_source.add_resource(Notice, '/notice')
api_source.add_resource(Checker, '/checker', '/checker/<string:checker_id>', '/checker/search')
api_source.add_resource(Bandwidth, '/bandwidth')
api_source.add_resource(BandwidthTemplates, '/bandwidth_templates')
api_source.add_resource(SnapshotImport, '/snapshot/import')
api_source.add_resource(SnapshotExport, '/snapshot/export/event', '/snapshot/export/<string:group_id>')
api_source.add_resource(Snapshot, '/snapshot/<string:snapshot_id>')
api_source.add_resource(
    Event,
    '/event',
    '/event/page/<int:page>',
    '/event/page/<int:page>/search',
    '/event/page/<int:page>/search/<string:search_str>',
    '/event/id/<string:event_id>',
    '/event/id/<string:event_id>/search',
    '/event/id/<string:event_id>/search/<string:search_str>',
    '/event/search',
    '/event/search/<string:search_str>',
    '/event/<string:channel>',
    '/event/<string:channel>/search',
    '/event/<string:channel>/search/<string:search_str>',
    '/event/<string:channel>/page/<int:page>',
    '/event/<string:channel>/page/<int:page>/search',
    '/event/<string:channel>/page/<int:page>/search/<string:search_str>',
    '/event/<string:channel>/id/<string:event_id>',
    '/event/<string:channel>/id/<string:event_id>/search',
    '/event/<string:channel>/id/<string:event_id>/search/<string:search_str>'
)
api_source.add_resource(EventExport, '/event/export', '/event/export/<string:event_id>')
api_source.add_resource(Channel, '/channel', '/channel/<string:mode>')
api_source.add_resource(StatusBar, '/statusbar', '/statusbar/<string:item_id>')
api_source.add_resource(EventFileInfo, '/event/fileinfo')
