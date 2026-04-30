from sqlalchemy import or_

from alchemy.model import Song, Radio
from alchemy.database import Session
from data import utils


class Factory:

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
        super().__init__(Song)

    def _make_object(self, *args):
        return Song(*args)

    def _make_objects(self, rows):
        return [self._make_object(*row) for row in rows]

    def fetch_many(self, condition):
        like = f"%{condition}%"
        return self.session.query(self.model).filter(
            or_(
                self.model.path.like(like),
                self.model.artist.like(like),
                self.model.album.like(like),
            )
        ).all()

    def list_dir(self, dir):
        songs_list = utils.list_dir(dir)
        return self._make_objects(songs_list)
