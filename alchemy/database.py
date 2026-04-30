"""Lazy SQLAlchemy engine + session factory for the PyMusic data layer.

Both the engine and the ``Session`` callable are created on first access so
that ``alchemy.config.connection_string`` can be a CWD-relative path without
the engine being bound to whichever directory happened to be active at import
time. Tests use this to redirect the database to a tmp dir per case.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alchemy import config
from alchemy.model import BaseObject

_engine = None
_Session = None


def _build_engine():
    return create_engine(f"sqlite:///{config.connection_string}", future=True)


class _LazyEngine:
    """Forwards every attribute lookup to a lazily-created SQLAlchemy Engine."""

    def __getattr__(self, name):
        global _engine
        if _engine is None:
            _engine = _build_engine()
        return getattr(_engine, name)


class _LazySession:
    """Same trick for ``sessionmaker``: build it on first call."""

    def __call__(self, *args, **kwargs):
        global _Session
        if _Session is None:
            _Session = sessionmaker(bind=engine, future=True)
        return _Session(*args, **kwargs)


engine = _LazyEngine()
Session = _LazySession()


def reset_engine():
    """Drop the cached engine + session so the next call rebuilds them.

    Useful for tests that change the working directory or the
    ``connection_string`` between cases.
    """
    global _engine, _Session
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _Session = None


def init_db():
    """Create every table declared on :data:`BaseObject` if it doesn't exist."""
    global _engine
    if _engine is None:
        _engine = _build_engine()
    BaseObject.metadata.create_all(_engine)
