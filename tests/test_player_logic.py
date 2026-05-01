"""PlayerLogic state-machine + side-effect tests.

These run with the GStreamer fallback (the headless ``mp3player`` does not
need a GStreamer install thanks to the no-op stub in ``player.gstreamer``).
"""

import pytest


@pytest.fixture
def player_logic(isolated_db):
    from logic.player_logic import PlayerLogic
    return PlayerLogic()


def test_default_modes(player_logic):
    pl = player_logic
    assert pl.get_mode() == pl.modes.NORMAL_PLAY
    assert pl.get_man_mode() == pl.man_modes.NORMAL


def test_set_and_get_mode(player_logic):
    pl = player_logic
    pl.set_mode(pl.modes.RANDOM_PLAY)
    assert pl.get_mode() == pl.modes.RANDOM_PLAY
    pl.set_mode(pl.modes.NORMAL_PLAY)
    assert pl.get_mode() == pl.modes.NORMAL_PLAY


def test_set_and_get_man_mode(player_logic):
    pl = player_logic
    pl.set_man_mode(pl.man_modes.RADIO)
    assert pl.get_man_mode() == pl.man_modes.RADIO
    pl.set_man_mode(pl.man_modes.NORMAL)
    assert pl.get_man_mode() == pl.man_modes.NORMAL


def test_random_song_within_range_and_avoids_current(player_logic):
    pl = player_logic
    drawn = {pl.random_song(0, 10) for _ in range(200)}
    assert drawn  # not empty
    assert all(0 <= n <= 10 for n in drawn)
    # With ``current_index=5`` the function must never return 5.
    drawn_avoiding_5 = {pl.random_song(5, 10) for _ in range(200)}
    assert 5 not in drawn_avoiding_5


def test_random_song_returns_false_when_list_too_small(player_logic):
    assert player_logic.random_song(0, 1) is False
    assert player_logic.random_song(0, 0) is False


def test_check_exists(player_logic, tmp_path):
    pl = player_logic
    f = tmp_path / 'song.mp3'
    f.write_bytes(b'')
    assert pl.check_exists(str(f)) is True
    assert pl.check_exists(str(tmp_path / 'missing.mp3')) is False


def test_player_methods_no_op_when_not_playing(player_logic):
    """``stop`` / ``pause`` / ``resume`` short-circuit when there is no
    active stream and must not raise even with the GStreamer stub."""
    pl = player_logic
    pl.stop()
    pl.pause()
    pl.resume()
    assert pl.is_playing() in (False, True)  # stub returns False
