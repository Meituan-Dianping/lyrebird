import json
import math
import datetime
import traceback
import time
from queue import Queue
from pathlib import Path
from lyrebird import application
from lyrebird import log
from lyrebird.utils import JSONFormat
from lyrebird.base_server import ThreadServer
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.hybrid import hybrid_property
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
    def __init__(self, path=None):
        self.database_uri = None
        super().__init__()

        if not path or path.isspace():
            ROOT_DIR = application.root_dir()
            DEFAULT_NAME = 'lyrebird.db'
            self.database_uri = ROOT_DIR/DEFAULT_NAME
        else:
            self.database_uri = Path(path).expanduser().absolute()

        self.init_engine()

        # init queue
        self.storage_queue = Queue()

        # subscribe all channel
        application.server['event'].subscribe('any', self.event_receiver)

    def init_engine(self):
        sqlite_path = 'sqlite:///'+str(self.database_uri)+'?check_same_thread=False'

        engine = create_engine(str(sqlite_path))

        # Set pragma on connect
        # https://www.sqlite.org/pragma.html
        event.listen(engine, 'connect', self._fk_pragma_on_connect)

        # Create all tables
        Base.metadata.create_all(engine)
        # Create session factory
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        self._scoped_session = Session

        logger.info(f'Init DB engine: {self.database_uri}')

    def _fk_pragma_on_connect(self, dbapi_con, con_record):
        # https://www.sqlite.org/pragma.html#pragma_journal_mode
        dbapi_con.execute('PRAGMA journal_mode=MEMORY')
        # https://www.sqlite.org/pragma.html#pragma_synchronous
        dbapi_con.execute('PRAGMA synchronous=OFF')

    def event_receiver(self, event, channel=None, event_id=None):
        # event is decoded , which should be encoded when save
        # event is deepcopy when created, no needs to copy again
        if channel == 'flow':
            application.encoders_decoders.encoder_handler(event['flow'])

        content = json.dumps(event, ensure_ascii=False)
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
        _subquery = session.query(Event.id).order_by(Event.id.desc())
        if len(channel_rules) > 0:
            _subquery = _subquery.filter(Event.channel.in_(channel_rules))
        _subquery = _subquery.offset(offset).limit(limit).subquery()
        result = session.query(Event).filter(Event.id == _subquery.c.id).all()
        self._scoped_session.remove()
        return result

    def get_page_index_by_event_id(self, event_id, channel_rules, limit=20):

        session = self._scoped_session()
        _subquery = session.query(Event).filter(Event.event_id == event_id).subquery()
        query = session.query(Event.id)
        if len(channel_rules) > 0:
            query = query.filter(Event.channel.in_(channel_rules))
        # Fix bug: event_id in page end, return next page
        # Wrong code: query.filter(Event.id>=subquery.c.id).count()
        result = query.filter(Event.id > _subquery.c.id).count()
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
        return math.ceil(result / page_size)

    def reset(self):
        self.stop()
        self.database_uri.unlink()
        self.init_engine()
        # TODO After self.stop() could terminate Thread, change `self.running = True` into self.start()
        self.running = True



class Event(Base, JSONFormat):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(16), index=True)
    event_id = Column(String(32), index=True)
    content = Column(Text)
    _timestamp = Column('timestamp', DateTime(timezone=True), default=datetime.datetime.utcnow)

    @hybrid_property
    def timestamp(self):
        seconds_offset = time.localtime().tm_gmtoff
        return self._timestamp.timestamp() + seconds_offset

