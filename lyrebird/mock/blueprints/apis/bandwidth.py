from flask_restful import Resource,request
from lyrebird import application
from lyrebird import log
logger = log.get_logger()


class Conf:
    def __init__(self):
        self.bandwidth = -1
        self.bandwidth_templates = [
            {
                "template_name": "UNLIMITED",
                "bandwidth": -1,
                "display": "UNLIMITED"
            },
            {
                "template_name": "2G",
                "bandwidth": 10,
                "display": "2G (10 Kb/s)"
            }, {
                "template_name": "2.5G",
                "bandwidth": 35,
                "display": "2.5G (35 Kb/s)"
            },
            {
                "template_name": "3G",
                "bandwidth": 120,
                "display": "3G (120 Kb/s)"
            }
        ]
        self.indexes_by_name = {
            i["template_name"]: i["bandwidth"] for i in self.bandwidth_templates}
config = Conf()

class Bandwidth(Resource):
    """
    网络带宽
    """
    def get(self):
        return application.make_ok_response(
            bandwidth=config.bandwidth
        )
    def put(self):
        template = request.json["templateName"]
        # check template valid
        if template in list(config.indexes_by_name.keys()):
            # reset bandwidth
            config.bandwidth = config.indexes_by_name[template]
            logger.debug(f'Modified bandwidth: {config.bandwidth}')
            return application.make_ok_response(bandwidth=config.bandwidth)
        else:
            return application.make_fail_response(msg=f'invalid template ! request data is {template}')

class BandwidthTemplates(Resource):
    """
    网络带宽模板列表
    """
    def get(self):
        return application.make_ok_response(
            bandwidth_templates=config.bandwidth_templates
        )

