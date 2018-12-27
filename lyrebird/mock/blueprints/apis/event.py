from flask_restful import Resource
from lyrebird.mock import context
from flask import request, jsonify, abort
from lyrebird import application

class Event(Resource):

    def post(self):
        msg = request.json.get('eventInfo')

        for action in msg.get('actions'):
            if action.get('type') == 'carrier':
                
                carrier_message = action.get('box', {})
                issue_channel = carrier_message.get('channel')
                issue_message = carrier_message.get('message')
                issue_state = carrier_message.get('state')
                
                issue_message['sender'] = msg.get('sender')
                
                application.server['event'].publish(issue_channel, issue_message, state=issue_state)
        return context.make_ok_response()
