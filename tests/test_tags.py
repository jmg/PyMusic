"""Tag handling tests."""

from __future__ import annotations

from pathlib import Path

from pymusic import tags


def test_format_duration() -> None:
    assert tags.format_duration(0) == "0:00"
    assert tags.format_duration(45) == "0:45"
    assert tags.format_duration(125) == "2:05"
    assert tags.format_duration(3725) == "1:02:05"


def test_read_tags_handles_missing_file(tmp_path: Path) -> None:
    info = tags.read_tags(tmp_path / "nope.mp3")
    assert info.title == "nope"
    assert info.artist == ""


def test_read_tags_falls_back_to_stem(tmp_path: Path) -> None:
    f = tmp_path / "Some Cool Track.mp3"
    f.write_bytes(b"\x00\x00")  # not a real MP3 — mutagen returns None
    info = tags.read_tags(f)
    assert info.title == "Some Cool Track"
