import json
from flask_restful import Resource
from flask import jsonify, request
from lyrebird import application

# Default event page size
PAGE_SIZE = 20


class Event(Resource):

    def get(self, channel=None, page=0, event_id=None):
        db = application.server['db']
        channel_rules = []
        if channel:
            channel_rules = channel.split('+')
        if event_id:
            page = db.get_page_index_by_event_id(event_id, channel_rules, limit=PAGE_SIZE)
        events = db.get_event(channel_rules, offset=page*PAGE_SIZE, limit=PAGE_SIZE)
        page_count = db.get_page_count(channel_rules, page_size=PAGE_SIZE)
        result = []
        for event in events:
            event_str = event.json()

            # Import decoder for decoding the requested content
            if event_str.get('channel') == 'flow':
                content = json.loads(event_str['content'])
                application.encoders_decoders.decoder_handler(content['flow'])
                event_str['content'] = json.dumps(content, ensure_ascii=False)

            result.append(event_str)
        return application.make_ok_response(events=result, page=page, page_count=page_count, page_size=PAGE_SIZE)

    def post(self, channel):
        message = request.json
        event_manager = application.server['event']
        event_manager.publish(channel, message)
        return application.make_ok_response()

    def delete(self):
        db_server = application.server['db']
        db_server.reset()
        return application.make_ok_response()

class Channel(Resource):

    def get(self, mode=None):
        if not mode:
            db = application.server['db']
            channel_list = db.get_channel_list()
            return jsonify([item[0] for item in channel_list])

        elif mode == 'default':
            channel = application.config.get('event.default_channel', [])
            return application.make_ok_response(data=channel)
