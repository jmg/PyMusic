from sqlalchemy import Column, Integer, String

try:
    from sqlalchemy.orm import declarative_base
except ImportError:  # SQLAlchemy < 1.4
    from sqlalchemy.ext.declarative import declarative_base

BaseObject = declarative_base()


class Song(BaseObject):
    __tablename__ = 'songs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column('song', String(255))
    artist = Column('interpret', String(50))
    album = Column(String(50))
    year = Column(Integer)
    title = Column(String(120))
    duration = Column(Integer)        # seconds
    play_count = Column(Integer, default=0)
    added_at = Column(Integer)        # unix epoch
    last_played = Column(Integer)     # unix epoch

    def __init__(self, id=None, path='', artist='', album='', year='',
                 title='', duration=None, play_count=0,
                 added_at=None, last_played=None):
        self.id = id
        self.path = path
        self.artist = artist
        self.album = album
        self.year = year
        self.title = title
        self.duration = duration
        self.play_count = play_count or 0
        self.added_at = added_at
        self.last_played = last_played


class Radio(BaseObject):
    __tablename__ = 'radios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column('radio', String(255))
    artist = Column('interpret', String(50))
    album = Column(String(50))
    year = Column(Integer)

    def __init__(self, id=None, path='', artist='', album='', year=''):
        self.id = id
        self.path = path
        self.artist = artist
        self.album = album
        self.year = year


class Score(BaseObject):
    __tablename__ = 'scores'

    id = Column(Integer, primary_key=True, autoincrement=True)
    idSong = Column(Integer)
    score = Column(Integer)


class IndexSong(BaseObject):
    __tablename__ = 'IndexSongs'

    # No real primary key on the original schema; SQLAlchemy needs one to map
    # the table, so we treat ``indexSong`` as the PK (it is unique by use).
    indexSong = Column(Integer, primary_key=True)
    idSong = Column(Integer)
    currentlyList = Column(Integer)
