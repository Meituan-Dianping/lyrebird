from flask import request
from lyrebird import application
from flask_restful import Resource

class SettingsApi(Resource):

    def get(self, action):
        if action == 'list':
            resp_dict = {}
            for script_name, script in application.settings.items():
                if not script.inited:
                    continue
                if script.category_md5 not in resp_dict:
                    resp_dict[script.category_md5] = {
                        'category_md5': script.category_md5,
                        'category': script.category,
                        'scripts': []
                    }
                script_dict = {
                    'name': script.name,
                    'title': script.title,
                    'notice': script.notice,
                    'category': script.category
                }
                resp_dict[script.category_md5]['scripts'].append(script_dict)
            return application.make_ok_response(data=list(resp_dict.values()))
        elif action == 'detail':
            script_name = request.args.get('name')
            if not script_name:
                return application.make_fail_response('Get setting failed, the query \"name\" not found')
            script = application.settings.get(script_name)
            if not script:
                return application.make_fail_response(f'Get setting failed, {script_name} does not exist')
            resp_dict = {
                'name': script.name,
                'title': script.title,
                'notice': script.notice,
                'category': script.category,
                'language': script.language,
                'submitText': script.submit_text,
                'configs': script.getter()
            }
            return application.make_ok_response(data=resp_dict)

    def post(self):
        script_name = request.args.get('name')
        if not script_name:
            return application.make_fail_response('Get setting failed, the query \"name\" not found')

        script = application.settings.get(script_name)
        if not script:
            return application.make_fail_response(f'Get setting failed, {script_name} does not exist')

        resp = script.setter(request.json.get('data'))        

        if resp:
            return application.make_fail_response(str(resp))
        return application.make_ok_response()

    def delete(self):
        script_name = request.args.get('name')
        if not script_name:
            return application.make_fail_response('Get setting failed, the query \"name\" not found')

        script = application.settings.get(script_name)
        if not script:
            return application.make_fail_response(f'Get setting failed, {script_name} does not exist')

        resp = script.restore()        

        if resp:
            return application.make_fail_response(str(resp))
        return application.make_ok_response()
