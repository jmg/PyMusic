"""CLI smoke tests."""

from __future__ import annotations

from pathlib import Path

from pymusic import cli, library


def test_stats_command(temp_db: Path, capsys, tmp_path: Path) -> None:
    rc = cli.main(["--db", str(temp_db), "stats"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Songs" in out


def test_scan_then_search(temp_db: Path, capsys, tmp_path: Path) -> None:
    music = tmp_path / "m"
    music.mkdir()
    (music / "Artist - Title.mp3").write_bytes(b"\x00")
    cli.main(["--db", str(temp_db), "scan", str(music)])
    capsys.readouterr()
    rc = cli.main(["--db", str(temp_db), "search", "Title"])
    out = capsys.readouterr().out
    assert "Artist - Title" in out
    assert rc == 0


def test_radio_lifecycle(temp_db: Path, capsys) -> None:
    cli.main(["--db", str(temp_db), "radio", "add", "http://example/stream",
              "--name", "Test"])
    capsys.readouterr()
    cli.main(["--db", str(temp_db), "radios"])
    out = capsys.readouterr().out
    assert "Test" in out
    radios = library.fetch_radios()
    cli.main(["--db", str(temp_db), "radio", "remove", str(radios[0].id)])
    assert library.fetch_radios() == []
