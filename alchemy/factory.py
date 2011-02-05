from sqlalchemy import *
from model import *
from database import Session
from data import utils

class Factory(object):

    def __init__(self, model):
        self.session = Session()
        self.model = model

    def fetch_all(self):
        return self.session.query(self.model).all()

    def insert(self, obj, commit=True):
        self.session.add(obj)
        if commit:
            self.session.commit()

    def commit(self):
        self.session.commit()


class Factory_songs(Factory):

    def __init__(self):
        Factory.__init__(self, Song)

    def _make_object(self, *args):
        song = Song(*args)
        return song

    def _make_objects(self, rows):
        objetcs = []
        for row in rows:
            obj = self._make_object(*row)
            objetcs.append(obj)
        return objetcs

    def fetch_many(self, condition):
        return self.session.query(self.model).filter(
               or_(self.model.path.like("%" + condition + "%"),
                   self.model.artist.like("%" + condition + "%"),
                   self.model.album.like("%" + condition + "%")
                   )
               ).all()

    def list_dir(self, dir):
        songs_list = utils.list_dir(dir)
        return self._make_objects(songs_list)
