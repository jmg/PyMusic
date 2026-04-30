"""Database engine, session, and schema migration.

The legacy schema used ``songs(id, song, interpret, album, year)`` and
``radios(id, radio, interpret, album, year)``. We keep those table names
but add columns over time. Migrations are applied idempotently on engine
creation so an existing ``MusicaInYou.db`` keeps its rows.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
    event,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from .config import get_settings


class Base(DeclarativeBase):
    pass


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # `song` is the file path — kept for backward compatibility with legacy DB.
    path: Mapped[str] = mapped_column("song", String(300), nullable=False, index=True)
    artist: Mapped[str] = mapped_column("interpret", String(200), default="")
    album: Mapped[str] = mapped_column(String(200), default="")
    year: Mapped[str] = mapped_column(String(10), default="")
    # Columns added by the modernization migration:
    title: Mapped[str] = mapped_column(String(300), default="")
    genre: Mapped[str] = mapped_column(String(100), default="")
    track_number: Mapped[int] = mapped_column(Integer, default=0)
    duration: Mapped[float] = mapped_column(default=0.0)
    play_count: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[int] = mapped_column(Integer, default=0)
    added_at: Mapped[Optional[str]] = mapped_column(DateTime, nullable=True)
    last_played_at: Mapped[Optional[str]] = mapped_column(DateTime, nullable=True)

    @property
    def display_title(self) -> str:
        if self.title:
            return self.title
        return Path(self.path).stem

    def __repr__(self) -> str:
        return f"<Song id={self.id} {self.artist!r} - {self.display_title!r}>"


class Radio(Base):
    __tablename__ = "radios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # `radio` is the URL — kept for backward compatibility.
    url: Mapped[str] = mapped_column("radio", String(500), nullable=False)
    name: Mapped[str] = mapped_column("interpret", String(200), default="")
    genre: Mapped[str] = mapped_column("album", String(200), default="")
    bitrate: Mapped[str] = mapped_column("year", String(20), default="")

    def __repr__(self) -> str:
        return f"<Radio id={self.id} {self.name!r} {self.url!r}>"


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    created_at: Mapped[Optional[str]] = mapped_column(DateTime, nullable=True)

    items: Mapped[list["PlaylistItem"]] = relationship(
        back_populates="playlist",
        cascade="all, delete-orphan",
        order_by="PlaylistItem.position",
    )


class PlaylistItem(Base):
    __tablename__ = "playlist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False
    )
    song_id: Mapped[int] = mapped_column(
        ForeignKey("songs.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, default=0)

    playlist: Mapped[Playlist] = relationship(back_populates="items")
    song: Mapped[Song] = relationship()

    __table_args__ = (
        Index("ix_playlist_items_playlist_position", "playlist_id", "position"),
    )


# Columns we expect on the legacy `songs` and `radios` tables. If they're
# missing (legacy DB), we ALTER TABLE them in.
_SONG_LEGACY_COLUMNS = {
    "title": "VARCHAR(300) DEFAULT ''",
    "genre": "VARCHAR(100) DEFAULT ''",
    "track_number": "INTEGER DEFAULT 0",
    "duration": "FLOAT DEFAULT 0.0",
    "play_count": "INTEGER DEFAULT 0",
    "rating": "INTEGER DEFAULT 0",
    "added_at": "DATETIME",
    "last_played_at": "DATETIME",
}


def _existing_columns(connection, table: str) -> set[str]:
    rows = connection.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return {r[1] for r in rows}


def _migrate_legacy_schema(engine) -> None:
    """Add modernization columns to legacy songs/radios tables in place."""
    with engine.begin() as conn:
        existing_tables = {
            r[0] for r in conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
        }

        if "songs" in existing_tables:
            cols = _existing_columns(conn, "songs")
            for name, ddl in _SONG_LEGACY_COLUMNS.items():
                if name not in cols:
                    conn.execute(text(f"ALTER TABLE songs ADD COLUMN {name} {ddl}"))


_engine = None
_SessionFactory: sessionmaker[Session] | None = None


def get_engine(db_path: Path | str | None = None):
    """Return the singleton engine, creating tables and migrations on first use."""
    global _engine, _SessionFactory
    if _engine is not None and db_path is None:
        return _engine

    if db_path is None:
        db_path = get_settings().db_path
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    url = f"sqlite:///{db_path}"
    engine = create_engine(url, future=True)

    @event.listens_for(engine, "connect")
    def _enable_fk(dbapi_conn, _):  # noqa: ANN001
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    _migrate_legacy_schema(engine)
    Base.metadata.create_all(engine)

    _engine = engine
    _SessionFactory = sessionmaker(bind=engine, future=True, expire_on_commit=False)
    return engine


def get_session_factory() -> sessionmaker[Session]:
    if _SessionFactory is None:
        get_engine()
    assert _SessionFactory is not None
    return _SessionFactory


@contextmanager
def session_scope() -> Iterator[Session]:
    """Transactional session context manager."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_for_tests(db_path: Path | str) -> None:
    """Reset the cached engine — for tests with a temp DB."""
    global _engine, _SessionFactory
    _engine = None
    _SessionFactory = None
    get_engine(db_path)
