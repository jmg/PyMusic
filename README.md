# PyMusic

A modern music player and library manager.

PyMusic was originally a Python 2 / wxPython 2.x / GStreamer 0.10 / pygtk
application. This is a complete modernization to **Python 3.10+**, **PySide6
(Qt 6)**, **libVLC**, **mutagen** and **SQLAlchemy 2.x**, while preserving the
existing `MusicaInYou.db` library so no rows are lost.

## Features

- **Library**: recursive directory scan, full-text search across artist /
  title / album / genre, missing-file cleanup, library statistics
- **Playback**: play / pause / stop / next / previous / seek / volume
- **Modes**: shuffle (random) and repeat
- **Tag editor**: read and write tags via mutagen (mp3, flac, ogg, m4a…)
- **Radio streams**: add, remove, and play internet radio URLs
- **Lyrics**: automatic fetch from the lyrics.ovh API with on-disk cache
- **Playlist export**: copy songs matching a query into a folder up to a size
  budget (replaces the legacy "generate list" feature)
- **Database playlists**: create, list, and delete persistent playlists
- **CLI**: `pymusic scan`, `pymusic search`, `pymusic stats`, `pymusic gui`, …
- **Schema migration**: legacy `songs(song, interpret, …)` databases are
  upgraded in place with new columns; old data is preserved
- **Dark theme** by default

## Install

```sh
pip install -r requirements.txt
# Or, as a package:
pip install -e .
```

System requirements:

- Python 3.10+
- libVLC (`apt install vlc` or `brew install vlc`) for playback
- A Qt 6 platform (X11, Wayland, macOS, or Windows) for the GUI

## Run

GUI:

```sh
pymusic gui
# or
python -m pymusic gui
```

CLI:

```sh
pymusic scan ~/Music
pymusic search "depeche mode" --limit 10
pymusic stats
pymusic radio add https://stream.example/m3u --name "Metro"
pymusic radios
pymusic export "rock" /tmp/rockmix --max-mb 700
pymusic clean
```

Use a custom database:

```sh
pymusic --db ~/.local/share/pymusic/library.db stats
```

## Project layout

```
pymusic/
├── __init__.py
├── __main__.py        # python -m pymusic
├── cli.py             # argparse CLI
├── config.py          # paths and settings
├── db.py              # SQLAlchemy models + migration
├── library.py         # scanner, search, playlists, generator
├── lyrics.py          # lyrics.ovh fetcher with cache
├── player.py          # libVLC wrapper
├── tags.py            # mutagen-backed tag I/O
└── gui/
    ├── app.py         # QApplication entry point + dark theme
    ├── main_window.py # main window, transport controls
    ├── models.py      # QAbstractTableModel for songs / radios
    ├── dialogs.py     # tag editor, add radio, generate playlist
    └── workers.py     # Qt thread-pool helper
tests/                 # pytest suite (17 tests)
database/MusicaInYou.db  # legacy DB, schema-migrated on first open
```

## Test

```sh
pip install pytest
pytest
```

## What changed from the legacy version?

| Concern               | Legacy                                | Modern                            |
|-----------------------|---------------------------------------|-----------------------------------|
| Python                | 2.x                                   | 3.10+                             |
| GUI                   | wxPython 2.8 / pygtk                  | PySide6 (Qt 6)                    |
| Audio                 | GStreamer 0.10 / pygame               | libVLC (python-vlc)               |
| Tags                  | hand-rolled ID3v1 parser              | mutagen                           |
| Database              | raw SQL via pysqlite2 + SQLAlchemy    | SQLAlchemy 2.x ORM only           |
| SQL injection         | string interpolation in queries       | parameterized via ORM             |
| Lyrics                | scraping `letras.terra.com.br`        | lyrics.ovh API + on-disk cache    |
| Threads               | manual `wx.MutexGuiEnter()` patterns  | `QThreadPool` with signals        |
| Notifications         | pynotify (deprecated)                 | Qt status bar + window title      |
| Encoding              | manual Latin-1 byte juggling          | mutagen/Qt handle Unicode         |
| Tests                 | none                                  | 17 pytest tests                   |
| Packaging             | none                                  | `pyproject.toml`, console scripts |

The database file `database/MusicaInYou.db` is kept and migrated in place — a
legacy install with thousands of rows will simply gain new columns
(`title`, `genre`, `track_number`, `duration`, `play_count`, `rating`,
`added_at`, `last_played_at`) on first open.
