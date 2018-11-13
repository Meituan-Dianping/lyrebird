import json
import datetime
import lyrebird
from lyrebird.mock import context
from sqlalchemy import Column, Table
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Flow(Base):

    __tablename__ = 'flow'
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(16))
    content = Column(Text)
    ts = Column(DateTime(timezone=True), default=datetime.datetime.now)

    def __init__(self, channel, content):
        self.channel = channel
        self.content = content


class Reporter:
    @classmethod
    def create_table(cls):
        Base.metadata.create_all()

    @classmethod
    def start_sql(cls):
        lyrebird.subscribe('any', save_data, event=True)

def save_data(event):
    message, channel = event.message, event.channel
    content = json.dumps(message)
    data = Flow(channel, str(content))
    context.db.create_all()
    context.db.session.add(data)
    context.db.session.commit()
