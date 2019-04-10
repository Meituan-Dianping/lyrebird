from flask_restful import Resource
from flask import jsonify
from lyrebird import application


class Event(Resource):

    def get(self, channel=None, page=0):
        db = application.server['db']
        channel_rules = []
        if channel:
            channel_rules = channel.split('+')
        events = db.get_event(channel_rules, offset=page*20)
        result = []
        for event in events:
            event_str = event.json()
            result.append(event_str)
        return jsonify(result)


class Channel(Resource):

    def get(self):
        db = application.server['db']
        channel_list = db.get_channel_list()
        return jsonify([item[0] for item in channel_list])
