from flask_sqlalchemy import SQLAlchemy
from lyrebird.mock.table import Flow

class DataBase:
    def __init__(self, app):
        self._db = SQLAlchemy(app)
        self._db.init_app(app)

    @property
    def model(self):
        return self._db.Model

    @property
    def session(self):
        return self._db.session

    @property
    def create_all(self):
        return self._db.create_all
