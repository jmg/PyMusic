"""Common fixtures for the test suite.

The application currently writes its sqlite file to a path relative to the
working directory (``database/MusicaInYou.db``). Every test that touches the
DB uses :func:`isolated_db`, which moves to a fresh ``tmp_path`` and discards
any cached SQLAlchemy engine left over from a previous case.
"""

import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    """Run the test inside a clean tmp dir so sqlite writes are sandboxed."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "database").mkdir()

    from alchemy.database import reset_engine
    reset_engine()

    yield tmp_path

    reset_engine()


def _id3v1_block(title='', artist='', album='', year=''):
    """Build a 128-byte ID3v1 tag suitable for appending to an .mp3 file."""

    def _pad(s, n):
        return s.encode('utf-8')[:n].ljust(n, b'\x00')

    return (
        b'TAG'
        + _pad(title, 30)
        + _pad(artist, 30)
        + _pad(album, 30)
        + _pad(year, 4)
        + b'\x00' * 30  # comment
        + b'\x00'       # genre
    )


@pytest.fixture
def fake_mp3(tmp_path):
    """Factory that drops a fake .mp3 file (random bytes + ID3v1 tail) on disk.

    Returns a callable ``make(name, *, artist, album, year, title='')`` that
    yields the absolute path written.
    """

    def make(name, *, artist='', album='', year='', title='', parent=None):
        target = (parent or tmp_path) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        body = b'\xff' * 200
        target.write_bytes(body + _id3v1_block(title, artist, album, year))
        return target

    return make
