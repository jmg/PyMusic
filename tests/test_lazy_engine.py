"""Lazy SQLAlchemy engine wiring tests.

The application keeps its sqlite file at a CWD-relative path. The tests
exercise that the engine is built lazily, so changing the working directory
between runs (or between test cases) actually re-targets the database
file, instead of staying anchored to wherever the module was first imported.
"""

import importlib

import pytest


def test_engine_url_resolves_to_current_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'database').mkdir()

    from alchemy import database
    database.reset_engine()

    url = str(database.engine.url)
    assert url.endswith('database/MusicaInYou.db'), url


def test_init_db_creates_every_model_table(isolated_db):
    from sqlalchemy import text
    from alchemy.database import engine, init_db

    init_db()
    with engine.connect() as conn:
        rows = conn.execute(
            text("select name from sqlite_master where type='table'"))
        tables = {row[0] for row in rows}
    # Lower-cased / actual table names declared in alchemy.model.
    assert {'songs', 'radios', 'scores', 'IndexSongs'}.issubset(tables)


def test_reset_engine_repoints_after_chdir(tmp_path, monkeypatch):
    """A second test directory should get its own physical sqlite file."""
    from alchemy.database import init_db, reset_engine

    a = tmp_path / 'a'
    (a / 'database').mkdir(parents=True)
    monkeypatch.chdir(a)
    reset_engine()
    init_db()
    assert (a / 'database' / 'MusicaInYou.db').exists()

    b = tmp_path / 'b'
    (b / 'database').mkdir(parents=True)
    monkeypatch.chdir(b)
    reset_engine()
    init_db()
    assert (b / 'database' / 'MusicaInYou.db').exists()


def test_engine_attribute_proxy_supports_connect(isolated_db):
    """``engine`` is a lazy proxy; basic operations must still work."""
    from sqlalchemy import text
    from alchemy.database import engine, init_db

    init_db()
    with engine.connect() as conn:
        result = conn.execute(text('select 1')).scalar()
    assert result == 1
