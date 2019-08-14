import json
import math
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

    def event_receiver(self, event, channel=None, event_id=None):
        content = json.dumps(event)
        flow = Event(event_id=event_id, channel=channel, content=content)
        self.storage_queue.put(flow)

    def run(self):
        session = self._scoped_session()
        while self.running:
            try:
                event = self.storage_queue.get()
                session.add(event)
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
        query = session.query(Event).order_by(Event.id.desc())
        if len(channel_rules) > 0:
            query = query.filter(Event.channel.in_(channel_rules))
        query = query.offset(offset).limit(limit)
        result = query.all()
        self._scoped_session.remove()
        return result

    def get_page_index_by_event_id(self, event_id, channel_rules, limit=20):
        session = self._scoped_session()
        subquery = session.query(Event).filter(Event.event_id==event_id).subquery()
        query = session.query(Event.id)
        if len(channel_rules) > 0:
            query = query.filter(Event.channel.in_(channel_rules))
        # Fix bug: event_id in page end, return next page
        # Wrong code: query.filter(Event.id>=subquery.c.id).count()
        result = query.filter(Event.id>subquery.c.id).count()
        return int(result/limit)

    def get_channel_list(self):
        session = self._scoped_session()
        result = session.query(Event.channel) \
            .group_by(Event.channel) \
            .all()
        self._scoped_session.remove()
        return result

    def get_page_count(self, channel_rules, page_size=20):
        session = self._scoped_session()
        query = session.query(Event.id)
        if len(channel_rules) > 0:
            query = query.filter(Event.channel.in_(channel_rules))
        result = query.count()
        self._scoped_session.remove()
        return math.ceil(result/page_size)


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
                prop_collection[prop] = prop_obj.timestamp()
        return prop_collection


class Event(Base, JSONFormat):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(16), index=True)
    event_id = Column(String(32), index=True)
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), default=datetime.datetime.now)
