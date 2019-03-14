from flask import Blueprint, request
from flask_restful import Resource, Api
from .common import Status, WorkMode, Manifest
from .flow import Flow, FlowList
from .mock import MockData, MockGroup, ActivatedMockGroup , MockGroupByName
from .config import Conf, ResetConf
from .plugin import Plugin
from .menu import Menu
from .event import Event
from .checker import Checker
from lyrebird.log import get_logger


logger = get_logger()


api = Blueprint('api', __name__, url_prefix='/api')
api_source = Api(api)

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
api_source.add_resource(FlowList, '/flow')
api_source.add_resource(MockGroup, '/mock', '/mock/<string:group_id>')
api_source.add_resource(MockData, '/mock/<string:group_id>/data', '/mock/<string:group_id>/data/<string:data_id>')
api_source.add_resource(ActivatedMockGroup, '/mock/activated', '/mock/<string:group_id>/<string:action>')
api_source.add_resource(MockGroupByName, '/mock_by_name')
api_source.add_resource(Conf, '/conf/<string:plugin_name>')
api_source.add_resource(ResetConf, '/conf/<string:plugin_name>/reset')
api_source.add_resource(WorkMode, '/mode', '/mode/<string:mode>')
api_source.add_resource(Plugin, '/plugin', '/plugin/<string:plugin_name>')
api_source.add_resource(Menu, '/menu')
api_source.add_resource(Event, '/event')
api_source.add_resource(Checker, '/checker', '/checker/<string:checker_id>')
