"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def temp_db(tmp_path: Path):
    """Use a fresh sqlite database for each test."""
    from pymusic import config, db

    db_path = tmp_path / "library.db"
    config.configure(db_path)
    db.reset_for_tests(db_path)
    yield db_path
