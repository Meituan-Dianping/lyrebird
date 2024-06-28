import json
import math
import datetime
import traceback
import time
import copy
from pathlib import Path
from lyrebird import application
from lyrebird import log
from lyrebird.utils import convert_size, convert_size_to_byte, JSONFormat
from lyrebird.base_server import ThreadServer
from lyrebird.mock import context
from sqlalchemy import event, and_
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Text, DateTime, create_engine, Table, MetaData
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.exc import OperationalError


"""
Database server

Worked as a background thread
storage all event message into database
"""

logger = log.get_logger()

Base = declarative_base()


class LyrebirdDatabaseServer(ThreadServer):
    def __init__(self, path=None):
        self.database_uri = None
        self.error_log = []
        self.error_log_threshold = application.config.get('event.db_connection_recover_threshold', 0)
        super().__init__()

        if not path or path.isspace():
            ROOT_DIR = application.root_dir()
            DEFAULT_NAME = 'lyrebird.db'
            self.database_uri = ROOT_DIR/DEFAULT_NAME
        else:
            self.database_uri = Path(path).expanduser().absolute()
        
        # Check whether the current database is broken
        personal_config = application._cm.personal_config
        if str(self.database_uri) in personal_config["event.broken_database_path_list"]:
            if self.database_uri.exists():
                self.database_uri.unlink()
                logger.warning(f"The broken DB has been deleted: {self.database_uri}")
            personal_config["event.broken_database_path_list"].remove(str(self.database_uri))
            application._cm.update_personal_config(personal_config)

        init_engine_success = self.init_engine()
        if not init_engine_success:
            logger.error("Lyrebird database has been broken! Current startup has been stopped, please restart Lyrebird.")
            logger.warning("Restarting will delete the broken database by default, historical events in inspector-pro will be lost, please be careful.")

        # init queue
        self.storage_queue = application.sync_manager.get_queue()

        # subscribe all channel
        application.server['event'].subscribe({
            'name': 'event_receiver',
            'origin': self,
            'channel': 'any',
            'func': self.event_receiver
        })
    
    def auto_alter_tables(self, engine):
        metadata = MetaData()
        tables = {
            table_name: {
                column.name: column for column in Table(table_name, metadata, autoload=True, autoload_with=engine).c
            }
            for table_name in engine.table_names()
        }
        for model_class in Base.__subclasses__():
            table_name = model_class.__table__.name
            if table_name not in tables:
                continue
            table = tables[table_name]
            for attr_name in dir(model_class):
                try:
                    attr = getattr(model_class, attr_name)
                except:
                    logger.warning(f'[Local DB]Cannot get attr:{attr_name} from {model_class}')
                    continue
                if not isinstance(attr, InstrumentedAttribute):
                    continue
                if not hasattr(attr, 'type'):
                    continue
                if not hasattr(attr, 'compile'):
                    continue
                attr_name = attr.name 
                if attr_name in table:
                    continue
                column_type = attr.type.compile(dialect=engine.dialect)
                engine.execute(f'ALTER TABLE {table_name} ADD COLUMN {attr_name} {column_type}')

    def init_engine(self):
        sqlite_path = 'sqlite:///'+str(self.database_uri)+'?check_same_thread=False'

        engine = create_engine(str(sqlite_path))

        # Set pragma on connect
        # https://www.sqlite.org/pragma.html
        event.listen(engine, 'connect', self._fk_pragma_on_connect)

        # Create all tables
        try:
            Base.metadata.create_all(engine)
        except Exception:
            # sqlalchemy.exc.DatabaseError (sqlite3.DatabaseError)
            personal_config = application._cm.personal_config
            personal_config["event.broken_database_path_list"].append(str(self.database_uri))
            application._cm.update_personal_config(personal_config)
            logger.info(f'{traceback.format_exc()}')
            return False
        
        # Create session factory
        session_factory = sessionmaker(bind=engine)
        Session = scoped_session(session_factory)
        self._scoped_session = Session
        self.auto_alter_tables(engine=engine)

        logger.info(f'Init DB engine: {self.database_uri}')
        return True

    def _fk_pragma_on_connect(self, dbapi_con, con_record):
        # https://www.sqlite.org/pragma.html#pragma_journal_mode
        dbapi_con.execute('PRAGMA journal_mode=MEMORY')
        # https://www.sqlite.org/pragma.html#pragma_synchronous
        dbapi_con.execute('PRAGMA synchronous=OFF')

    def event_receiver(self, event, channel=None, event_id=None):
        # event is decoded , which should be encoded when save
        # deepcopy to avoid affecting checker running
        if channel == 'flow':
            event = copy.deepcopy(event)
            application.encoders_decoders.encoder_handler(event['flow'])

        content = json.dumps(event, ensure_ascii=False)
        if isinstance(event, dict):
            message = event.get('message')
        else:
            message = None
        flow = Event(event_id=event_id, channel=channel, content=content, message=message)
        self.storage_queue.put(flow)

    def start(self):
        super().start()

    def run(self):
        session = self._scoped_session()
        while self.running:
            try:
                event = self.storage_queue.get()
                if event is None:
                    break
                session.add(event)
                session.commit()
                context.emit('db_action', 'add event log')
            except OperationalError as e:
                logger.error(f'Save event failed. {traceback.format_exc()}')
                self.error_log.append(e)
                if len(self.error_log) > self.error_log_threshold:
                    logger.warning(f'DB would be reset: {self.database_uri}')
                    self.error_log = []
                    self.reset()
                    session = self._scoped_session()
                else:
                    session.rollback()
            except Exception:
                logger.error(f'Save event failed. {traceback.format_exc()}')
                session.rollback()

    def stop(self):
        super().stop()

    @property
    def session(self):
        return self._scoped_session()

    def get_event(self, channel_rules, offset=0, limit=20, search_str=''):
        search_str_list = [item.strip() for item in search_str.strip().split('+')] if search_str else []
        session = self._scoped_session()
        _subquery = session.query(Event.id).order_by(Event.id.desc())
        if len(channel_rules) > 0:
            _subquery = _subquery.filter(Event.channel.in_(channel_rules))
        if len(search_str_list) > 0:
            _subquery = _subquery.filter(Event.message != None)
            and_cond = []
            for search_str in search_str_list:
                and_cond.append(Event.message.like(f'%%{search_str}%%'))
            _subquery = _subquery.filter(and_(*and_cond))
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

    def get_page_count(self, channel_rules, page_size=20, search_str=''):
        session = self._scoped_session()
        query = session.query(Event.id)
        search_str_list = [item.strip() for item in search_str.strip().split('+')] if search_str else []
        if len(channel_rules) > 0:
            query = query.filter(Event.channel.in_(channel_rules))
        if len(search_str_list) > 0:
            query = query.filter(Event.message != None)
            and_cond = []
            for search_str in search_str_list:
                and_cond.append(Event.message.like(f'%%{search_str}%%'))
            query = query.filter(and_(*and_cond))
        result = query.count()
        self._scoped_session.remove()
        return math.ceil(result / page_size)
    
    def get_database_info(self):
        database_path = str(self.database_uri)
        size = self.database_uri.stat().st_size
        readable_size = convert_size(size)
        database_info = {
            'path': database_path,
            'size': readable_size,
            'oversized': False
        }

        threshold_str = application._cm.config.get('event.file_size_threshold')
        if threshold_str is not None:
            threshold_byte = convert_size_to_byte(threshold_str)
            oversized = threshold_byte and size > threshold_byte
            database_info['threshold'] = threshold_str
            database_info['oversized'] = oversized
        
        return database_info

    def reset(self):
        self.stop()
        self.database_uri.unlink()
        self.init_engine()
        if not self.server_thread.is_alive():
            self.start()
        self.running = True


class Event(Base, JSONFormat):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(16), index=True)
    event_id = Column(String(32), index=True)
    content = Column(Text)
    message = Column(Text, default=None)
    _timestamp = Column('timestamp', DateTime(timezone=True), default=datetime.datetime.utcnow)

    @hybrid_property
    def timestamp(self):
        seconds_offset = time.localtime().tm_gmtoff
        return self._timestamp.timestamp() + seconds_offset
