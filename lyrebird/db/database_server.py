import json
import datetime
import traceback
from queue import Queue
from lyrebird import application
from lyrebird.base_server import ThreadServer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Text, DateTime, create_engine

"""
Database server

Worked as a backgrund thread
storage all event message into database
"""

Base = declarative_base()

class LyrebirdDatabaseServer(ThreadServer):
    def __init__(self):
        super().__init__()

        # init sqlite
        DB_FILE_NAME = 'lyrebird.db'
        ROOT_DIR = application.root_dir()
        SQLALCHEMY_DATABASE_URI = ROOT_DIR/DB_FILE_NAME
        sqlite_path = 'sqlite:///'+str(SQLALCHEMY_DATABASE_URI)
        # TODO: 'sqlite:///' is unfriendly to windows

        engine = create_engine(str(sqlite_path))
        Base.metadata.create_all(engine)

        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

        # init queue
        self.storage_queue = Queue()
        
        # subscribe all channel
        application.server['event'].subscribe('any', self.put_queue, event=True)

    def put_queue(self, event):
        message, channel = event.message, event.channel
        content = json.dumps(message)
        flow = FLow(channel=channel, content=content)
        self.storage_queue.put(flow)

    def run(self):
        while self.running:
            try:
                flow = self.storage_queue.get()
                self.session.add(FLow(channel=flow.channel, content=flow.content))
                self.session.commit()
            except Exception:
                traceback.print_exc()

    def stop(self):
        super().stop()


class FLow(Base):
    __tablename__ = 'flow'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel = Column(String(16))
    content = Column(Text)
    ts = Column(DateTime(timezone=True), default=datetime.datetime.now)
