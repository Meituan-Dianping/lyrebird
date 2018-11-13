import json
import datetime
import lyrebird
from lyrebird.mock import context
from sqlalchemy import Column, Table, String, Integer, DateTime, Text


class Flow(context.db.model):

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(16))
    content = Column(Text)
    ts = Column(DateTime(timezone=True), default=datetime.datetime.now)

    def __init__(self, channel, content):
        self.channel = channel
        self.content = content

def start_sql():
    lyrebird.subscribe('any', save_data, event=True)
    context.db.create_all()

def save_data(event):
    message, channel = event.message, event.channel
    content = json.dumps(message)
    data = Flow(channel, str(content))
    context.db.create_all()
    context.db.session.add(data)
    context.db.session.commit()
