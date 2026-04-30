"""Smoke-test that every importable module loads cleanly under Python 3.

Modules that depend on optional system libraries (wxPython, PyGObject) are
intentionally excluded; their underlying behaviour is exercised by the
runtime, not by unit tests.
"""

import importlib

import pytest

PURE_MODULES = [
    "generics.multiprogramming",
    "logic.config",
    "logic.tags",
    "logic.tagsNew",
    "data.config",
    "data.connection",
    "data.utils",
    "data.clases.clases",
    "alchemy.config",
    "alchemy.model",
    "alchemy.database",
    "alchemy.factory",
    "lyrics.utils",
    "lyrics.terra",
    "lyrics.engine",
    "visual.fractals.lindenmayer",
    "visual.fractals.FractalGen",
    "interfaces.configuration",
    "interfaces.Notify",
    "player.gstreamer",
    "player.mp3player",
]


@pytest.mark.parametrize("module_name", PURE_MODULES)
def test_module_imports(module_name):
    importlib.import_module(module_name)


def test_db_imports_with_isolation(isolated_db):
    """``data.db`` and ``data.SongsFactory`` should import + create tables."""
    importlib.import_module("data.db")
    importlib.import_module("data.SongsFactory")
    importlib.import_module("data.RadiosFactory")
    importlib.import_module("logic.player_logic")
    importlib.import_module("interfaces.console")
