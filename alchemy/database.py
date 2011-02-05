from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlite3 import dbapi2 as sqlite

from alchemy import config

Base = declarative_base()

engine = create_engine('sqlite:///' + config.connection_string, module=sqlite)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)


