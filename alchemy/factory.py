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

    def delete_by_id(self, id):
        obj = self.session.query(self.model).get(id)
        if obj is not None:
            self.session.delete(obj)
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

    def list_files(self, paths):
        songs_list = utils.list_files(paths)
        return self._make_objects(songs_list)

    def bump_play_count(self, song_id):
        import time as _t
        obj = self.session.query(self.model).get(song_id)
        if obj is not None:
            obj.play_count = (obj.play_count or 0) + 1
            obj.last_played = int(_t.time())
            self.session.commit()

    def smart_filter(self, kind, limit=200):
        q = self.session.query(self.model)
        if kind == "recent":
            q = q.order_by(self.model.added_at.desc().nullslast())
        elif kind == "most_played":
            q = q.filter((self.model.play_count != None) & (self.model.play_count > 0))  # noqa: E711
            q = q.order_by(self.model.play_count.desc())
        elif kind == "never_played":
            q = q.filter((self.model.play_count == None) | (self.model.play_count == 0))  # noqa: E711
        elif kind == "last_played":
            q = q.filter(self.model.last_played != None).order_by(  # noqa: E711
                self.model.last_played.desc()
            )
        return q.limit(limit).all()
