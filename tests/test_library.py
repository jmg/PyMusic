"""Library scanner / search / generator tests."""

from __future__ import annotations

from pathlib import Path

from pymusic import library


def _make_song_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x00\x00")  # contents don't matter; mutagen tolerates failures


def test_scan_directory_imports_audio_files(temp_db: Path, tmp_path: Path) -> None:
    music = tmp_path / "music"
    _make_song_file(music / "Artist - Track 1.mp3")
    _make_song_file(music / "subdir" / "Track 2.flac")
    _make_song_file(music / "ignored.txt")

    progress = library.scan_directory(music)
    assert progress.added == 2
    assert progress.skipped == 0

    songs = library.fetch_all_songs()
    assert {Path(s.path).name for s in songs} == {"Artist - Track 1.mp3", "Track 2.flac"}


def test_scan_skips_existing(temp_db: Path, tmp_path: Path) -> None:
    music = tmp_path / "music"
    _make_song_file(music / "a.mp3")
    library.scan_directory(music)
    progress = library.scan_directory(music)
    assert progress.added == 0
    assert progress.skipped == 1


def test_search_returns_matching_songs(temp_db: Path, tmp_path: Path) -> None:
    from pymusic.db import Song, session_scope

    with session_scope() as session:
        session.add(Song(path="/m/a.mp3", title="Enjoy The Silence",
                         artist="Depeche Mode", album="Violator"))
        session.add(Song(path="/m/b.mp3", title="Smooth Criminal",
                         artist="Michael Jackson", album="Bad"))

    found = library.search_songs("violator")
    assert len(found) == 1
    assert found[0].artist == "Depeche Mode"

    found = library.search_songs("jackson")
    assert len(found) == 1


def test_radios_crud(temp_db: Path) -> None:
    radio = library.add_radio("https://example.com/stream", name="Test")
    assert radio.id is not None
    radios = library.fetch_radios()
    assert len(radios) == 1
    assert library.delete_radio(radio.id) is True
    assert library.fetch_radios() == []


def test_generate_playlist_respects_size(temp_db: Path, tmp_path: Path) -> None:
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    src.mkdir()
    # 3 files, ~1 MB each
    payload = b"x" * (1024 * 1024)
    for i in range(3):
        (src / f"track{i}.mp3").write_bytes(payload)

    library.scan_directory(src, read_tags=False)
    result = library.generate_playlist_to_dir(
        filter_query="track",
        destination=dest,
        max_size_mb=2,
    )
    assert result.copied == 2
    assert result.total_bytes <= 2 * 1024 * 1024
    assert sum(1 for _ in dest.iterdir()) == 2


def test_remove_missing_files(temp_db: Path, tmp_path: Path) -> None:
    real = tmp_path / "real.mp3"
    real.write_bytes(b"\x00")
    from pymusic.db import Song, session_scope

    with session_scope() as session:
        session.add(Song(path=str(real)))
        session.add(Song(path=str(tmp_path / "ghost.mp3")))

    removed = library.remove_missing_files()
    assert removed == 1
    assert len(library.fetch_all_songs()) == 1


def test_playlists(temp_db: Path) -> None:
    from pymusic.db import Song, session_scope

    with session_scope() as session:
        session.add_all([
            Song(path="/a.mp3", title="A"),
            Song(path="/b.mp3", title="B"),
        ])
        session.flush()
        ids = [s.id for s in session.query(Song).all()]

    pl = library.create_playlist("Mix", ids)
    assert library.list_playlists()[0].name == "Mix"
    songs = library.get_playlist_songs(pl.id)
    assert [s.title for s in songs] == ["A", "B"]

    library.add_to_playlist(pl.id, ids[0])
    assert len(library.get_playlist_songs(pl.id)) == 3

    library.delete_playlist(pl.id)
    assert library.list_playlists() == []


def test_stats(temp_db: Path, tmp_path: Path) -> None:
    music = tmp_path / "m"
    _make_song_file(music / "x.mp3")
    library.scan_directory(music)
    s = library.stats()
    assert s["songs"] == 1
    assert s["radios"] == 0
