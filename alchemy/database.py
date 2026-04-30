from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alchemy import config
from alchemy.model import BaseObject

engine = create_engine(f"sqlite:///{config.connection_string}", future=True)
BaseObject.metadata.create_all(engine)

Session = sessionmaker(bind=engine, future=True)
