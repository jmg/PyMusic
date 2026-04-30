"""Common fixtures for the smoke-test suite.

The application currently writes its sqlite file to a path relative to the
working directory (``database/MusicaInYou.db``). The tests run with that
working directory set to a tmp_path so they never touch the developer's data.
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

    # Drop any engine cached from a previous case; the next call rebuilds it
    # against the new CWD.
    from alchemy.database import reset_engine
    reset_engine()

    yield tmp_path

    reset_engine()
