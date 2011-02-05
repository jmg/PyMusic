from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

BaseObject = declarative_base()

class Song(BaseObject):
    __tablename__ = 'Songs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column('song', String(255))
    artist = Column('interpret', String(50))
    album = Column(String(50))
    year = Column(Integer)

    def __init__(self, id=None, path='', artist='', album='', year=''):
        self.id = id
        self.path = path
        self.artist = artist
        self.album = album
        self.year = year


class Radio(BaseObject):
    __tablename__ = 'Radios'

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column('song', String(255))
    artist = Column('interpret', String(50))
    album = Column(String(50))
    year = Column(Integer)

    def __init__(self, id=None, path='', artist='', album='', year=''):
        self.id = id
        self.path = path
        self.artist = artist
        self.album = album
        self.year = year
