from flask_sqlalchemy import SQLAlchemy

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

    def create_all(self):
        self._db.create_all()
