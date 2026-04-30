"""Database / model tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from pymusic import db


def test_engine_creates_tables(temp_db: Path) -> None:
    db.get_engine()
    with sqlite3.connect(temp_db) as conn:
        tables = {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")}
    assert "songs" in tables
    assert "radios" in tables
    assert "playlists" in tables
    assert "playlist_items" in tables


def test_legacy_schema_is_migrated(tmp_path: Path) -> None:
    """A legacy DB without modernization columns gets them added."""
    db_path = tmp_path / "legacy.db"
    with sqlite3.connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song VARCHAR(300) NOT NULL,
                interpret VARCHAR(100),
                album VARCHAR(100),
                year VARCHAR(10)
            );
            CREATE TABLE radios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                radio VARCHAR(300) NOT NULL,
                interpret VARCHAR(100),
                album VARCHAR(100),
                year VARCHAR(10)
            );
            INSERT INTO songs (song, interpret, album, year)
                VALUES ('/music/song.mp3', 'Artist', 'Album', '2020');
        """)
    from pymusic import config

    config.configure(db_path)
    db.reset_for_tests(db_path)

    with sqlite3.connect(db_path) as conn:
        cols = {r[1] for r in conn.execute("PRAGMA table_info(songs)")}
    assert "title" in cols
    assert "duration" in cols
    assert "play_count" in cols

    # Legacy row still readable through ORM
    with db.session_scope() as session:
        from sqlalchemy import select

        songs = list(session.execute(select(db.Song)).scalars())
    assert len(songs) == 1
    assert songs[0].artist == "Artist"
    assert songs[0].path == "/music/song.mp3"


def test_song_display_title_falls_back_to_filename() -> None:
    s = db.Song(path="/music/Cool Song.mp3")
    assert s.display_title == "Cool Song"
    s.title = "Real Title"
    assert s.display_title == "Real Title"
