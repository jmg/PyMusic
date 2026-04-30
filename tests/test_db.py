"""End-to-end checks against the unified SQLAlchemy-backed data layer."""

import pytest


@pytest.fixture
def db(isolated_db):
    from data.db import dataBase
    return dataBase()


def test_index_lifecycle(db):
    db.UpdateIndex(idSong=10, index=0)
    db.UpdateIndex(idSong=11, index=1)
    db.UpdateIndex(idSong=12, index=2)

    # Updating an existing index swaps the song, not duplicates it.
    db.UpdateIndex(idSong=99, index=1)

    db.ResetList()
    db.UpdateList(top=1)

    # No Songs rows exist yet so the join returns an empty list, but the
    # underlying mutations are validated through the IndexSong table directly.
    from sqlalchemy import text
    from alchemy.database import engine
    with engine.connect() as conn:
        rows = sorted(
            tuple(r) for r in conn.execute(
                text("select indexSong, idSong, currentlyList from IndexSongs"))
        )
    assert rows == [(0, 10, 1), (1, 99, 1), (2, 12, 0)]


def test_score_song_insert_and_update(db):
    db.scoreSong(idSong=1, score=4)
    db.scoreSong(idSong=2, score=2)
    db.scoreSong(idSong=1, score=5)  # update path

    from sqlalchemy import text
    from alchemy.database import engine
    with engine.connect() as conn:
        rows = sorted(
            tuple(r) for r in conn.execute(
                text("select idSong, score from scores order by idSong"))
        )
    assert rows == [(1, 5), (2, 2)]


def test_search_uses_parameter_binding_not_string_concat(db):
    """The previous raw-sqlite implementation interpolated user input directly
    into SQL; the SQLAlchemy port must bind parameters instead."""
    # A pathological condition that would have broken the old f-string SQL.
    rows = db.fetchManyWithId("'; drop table Songs; --")
    assert rows == []


def test_factories_roundtrip(isolated_db):
    """Insert via SongsFactory / RadiosFactory and read back via dataBase."""
    from data.clases.clases import Song
    from data.SongsFactory import SongsFactory
    from data.RadiosFactory import RadiosFactory
    from data.db import dataBase
    from alchemy.database import init_db

    init_db()

    sf = SongsFactory()
    sf.createTable()
    sf.insert(Song(id=None, path="/tmp/a.mp3", artist="Anon", album="X", year="2024"))
    sf.insert(Song(id=None, path="/tmp/b.mp3", artist="Anon", album="X", year="2024"))

    rf = RadiosFactory()
    rf.create_table()
    rf.insert("http://example.com/stream")

    db = dataBase()
    paths = sorted(row[1] for row in db.fetchManyWithId(""))
    assert paths == ["/tmp/a.mp3", "/tmp/b.mp3"]

    radios = rf.fetch_all()
    assert [r.path for r in radios] == ["http://example.com/stream"]
