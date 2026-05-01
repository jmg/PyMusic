"""End-to-end ConsoleProxy tests.

These mirror what happens when the user invokes ``run.py search foo`` /
``run.py play 0`` / ``run.py playlist`` from the command line. The audio
backend is replaced with a recording stub so the test runs offline.
"""

from __future__ import annotations

from typing import Any, List, Tuple

import pytest


class StubPlayer:
    """Recording stand-in for ``player.gstreamer.mp3player``.

    ``ConsolePlayer.play`` busy-loops on ``songFinished`` and exits on the
    first ``True`` so we keep that behaviour deterministic.
    """

    def __init__(self) -> None:
        self.calls: List[Tuple[str, Any]] = []

    def play(self, song):
        self.calls.append(('play', song))

    def stop(self):
        self.calls.append(('stop', None))

    def songFinished(self):
        return True


@pytest.fixture
def console_env(isolated_db, monkeypatch, capsys):
    """Set up a populated DB + stubbed player and return a small helper."""

    from alchemy.database import init_db
    from data.SongsFactory import SongsFactory
    from data.clases.clases import Song

    init_db()
    sf = SongsFactory()
    sf.createTable()
    sf.insert(Song(id=None, path='/library/foo-one.mp3', artist='Foo',
                   album='Album', year='2020'))
    sf.insert(Song(id=None, path='/library/foo-two.mp3', artist='Foo',
                   album='Album', year='2020'))
    sf.insert(Song(id=None, path='/library/bar-three.mp3', artist='Bar',
                   album='Album', year='2021'))

    from interfaces import console as console_mod

    stub = StubPlayer()
    # ConsolePlayer holds the player + dba as class attributes shared across
    # all ConsoleProxy instances; replacing the class attribute redirects
    # every consumer.
    monkeypatch.setattr(console_mod.ConsolePlayer, 'Player', stub)

    # Make sure the IndexSongs table exists in the current isolated DB.
    console_mod.ConsoleProxy.Player.dba.createIndexTable()

    class Helper:
        module = console_mod
        player = stub

        def run(self, *argv):
            console_mod.ConsoleProxy(list(argv))
            return capsys.readouterr()

    return Helper()


def test_search_lists_matches_and_records_index(console_env):
    out = console_env.run('search', 'Foo').out
    # Two matches were found and printed.
    assert 'foo-one.mp3' in out
    assert 'foo-two.mp3' in out
    assert 'bar-three.mp3' not in out
    # No play calls happen on a search.
    assert console_env.player.calls == []


def test_play_by_index_uses_indexed_song(console_env):
    """``search`` populates IndexSongs; ``play <n>`` resolves through it."""
    console_env.run('search', 'Foo')
    out = console_env.run('play', '0').out

    plays = [c for c in console_env.player.calls if c[0] == 'play']
    stops = [c for c in console_env.player.calls if c[0] == 'stop']
    assert len(plays) == 1, console_env.player.calls
    assert plays[0][1].endswith('foo-one.mp3') or plays[0][1].endswith('foo-two.mp3')
    assert len(stops) == 1
    assert 'Currently Playing' in out


def test_play_by_path_passthrough(console_env):
    """If the argument isn't an int, the path is played directly."""
    out = console_env.run('play', '/library/bar-three.mp3').out
    assert any(c == ('play', '/library/bar-three.mp3')
               for c in console_env.player.calls)
    assert 'bar-three.mp3' in out


def test_playlist_replays_every_currently_active_song(console_env):
    """``search`` marks all matches as ``currentlyList=1``; ``playlist``
    iterates over them, calling ``Player.play`` for each."""
    console_env.run('search', 'Foo')
    out = console_env.run('playlist').out

    plays = [c[1] for c in console_env.player.calls if c[0] == 'play']
    # Two songs matched 'Foo'; playlist plays them all.
    assert len(plays) == 2
    assert all(p.endswith('foo-one.mp3') or p.endswith('foo-two.mp3')
               for p in plays)
    assert 'TOTAL: 2' in out


def test_unknown_command_falls_back_to_default(console_env):
    out = console_env.run('not-a-command', 'arg').out
    assert 'not-a-command' in out
    # No song should have been played.
    assert all(c[0] != 'play' for c in console_env.player.calls)
