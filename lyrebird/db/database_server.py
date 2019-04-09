import json
import datetime
import traceback
from queue import Queue
from lyrebird import application
from lyrebird import log
from lyrebird.base_server import ThreadServer
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Text, DateTime, create_engine

"""
Database server

Worked as a backgrund thread
storage all event message into database
"""

logger = log.get_logger()

Base = declarative_base()


class LyrebirdDatabaseServer(ThreadServer):
    def __init__(self):
        super().__init__()

        DB_FILE_NAME = 'lyrebird.db'
        ROOT_DIR = application.root_dir()
        SQLALCHEMY_DATABASE_URI = ROOT_DIR/DB_FILE_NAME
        sqlite_path = 'sqlite:///'+str(SQLALCHEMY_DATABASE_URI)

        engine = create_engine(str(sqlite_path))
        # Create all tables
        Base.metadata.create_all(engine)
        # Create session factory
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        self._scoped_session = Session

        # init queue
        self.storage_queue = Queue()

        # subscribe all channel
        application.server['event'].subscribe('any', self.event_receiver)

    def event_receiver(self, event, channel=None):
        content = json.dumps(event)
        flow = Event(channel=channel, content=content)
        self.storage_queue.put(flow)

    def run(self):
        session = self._scoped_session()
        while self.running:
            try:
                event = self.storage_queue.get()
                session.add(Event(channel=event.channel, content=event.content))
                session.commit()
            except Exception:
                logger.error(f'Save event failed. {traceback.format_exc()}')

    def stop(self):
        super().stop()

    @property
    def session(self):
        return self._scoped_session()

    def get_event(self, channel_rules, offset=0, limit=20):
        session = self._scoped_session()
        result = session.query(Event) \
            .order_by(Event.id.desc()) \
            .filter(Event.channel.in_(channel_rules)) \
            .offset(offset) \
            .limit(limit) \
            .all()
        self._scoped_session.remove()
        return result

    def get_channel_list(self):
        session = self._scoped_session()
        result = session.query(Event.channel) \
            .group_by(Event.channel) \
            .all()
        self._scoped_session.remove()
        return result


class JSONFormat:

    def json(self):
        prop_collection = {}
        props = dir(self)
        for prop in props:
            if prop.startswith('_'):
                continue
            prop_obj = getattr(self, prop)
            if isinstance(prop_obj, (str, int, bool)):
                prop_collection[prop] = prop_obj
            elif isinstance(prop_obj, datetime.datetime):
                prop_collection[prop] = str(prop_obj)
        return prop_collection


class Event(Base, JSONFormat):
    __tablename__ = 'flow'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(16), index=True)
    content = Column(Text)
    ts = Column(DateTime(timezone=True), default=datetime.datetime.now)

