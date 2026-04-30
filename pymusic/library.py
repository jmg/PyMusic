"""Library management: scan, import, search, edit, and delete tracks.

This module is the equivalent of the legacy ``data/SongsFactory.py`` and
``logic/player_logic.py`` data plumbing — but stateless, transactional,
and tested. Filesystem scanning runs as a generator so large trees can
report progress to a UI.
"""

from __future__ import annotations

import datetime as _dt
import logging
import os
import shutil
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sqlalchemy import delete, func, or_, select

from . import tags as tagmod
from .config import get_settings
from .db import Playlist, PlaylistItem, Radio, Song, session_scope

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------


@dataclass
class ScanProgress:
    scanned: int = 0
    added: int = 0
    skipped: int = 0
    current_path: str = ""


def iter_audio_files(root: str | Path, extensions: Optional[Iterable[str]] = None) -> Iterator[Path]:
    """Yield every audio file under *root* (recursive, follows directories)."""
    settings = get_settings()
    exts = {e.lower() for e in (extensions or settings.audio_extensions)}
    root = Path(root)
    if not root.exists():
        return
    if root.is_file():
        if root.suffix.lower() in exts:
            yield root
        return
    for dirpath, _dirs, files in os.walk(root, followlinks=False):
        for name in files:
            if Path(name).suffix.lower() in exts:
                yield Path(dirpath, name)


def scan_directory(
    root: str | Path,
    *,
    read_tags: bool = True,
    on_progress: Optional[callable] = None,  # type: ignore[type-arg]
) -> ScanProgress:
    """Add every audio file under *root* to the library.

    Existing rows (matched by absolute path) are skipped without re-reading
    tags. Returns a :class:`ScanProgress` summary.
    """
    progress = ScanProgress()
    now = _dt.datetime.utcnow()

    with session_scope() as session:
        existing = {p for (p,) in session.execute(select(Song.path))}
        for path in iter_audio_files(root):
            progress.scanned += 1
            progress.current_path = str(path)
            sp = str(path)
            if sp in existing:
                progress.skipped += 1
            else:
                tag = tagmod.read_tags(path) if read_tags else tagmod.TagInfo(title=path.stem)
                song = Song(
                    path=sp,
                    title=tag.title,
                    artist=tag.artist,
                    album=tag.album,
                    year=tag.year,
                    genre=tag.genre,
                    track_number=tag.track_number,
                    duration=tag.duration,
                    added_at=now,
                )
                session.add(song)
                existing.add(sp)
                progress.added += 1
            if on_progress is not None and progress.scanned % 25 == 0:
                on_progress(progress)
        session.flush()

    if on_progress is not None:
        on_progress(progress)
    return progress


# ---------------------------------------------------------------------------
# Queries
# ---------------------------------------------------------------------------


def fetch_all_songs(order_by: str = "artist") -> list[Song]:
    valid = {
        "artist": (Song.artist, Song.album, Song.track_number),
        "album": (Song.album, Song.track_number),
        "title": (Song.title,),
        "added": (Song.added_at.desc(),),
        "play_count": (Song.play_count.desc(), Song.last_played_at.desc()),
        "path": (Song.path,),
    }
    cols = valid.get(order_by, valid["artist"])
    with session_scope() as session:
        result = session.execute(select(Song).order_by(*cols)).scalars().all()
        return list(result)


def search_songs(query: str) -> list[Song]:
    """Full-text-ish search across artist/title/album/path."""
    if not query.strip():
        return fetch_all_songs()
    pattern = f"%{query.strip()}%"
    with session_scope() as session:
        result = session.execute(
            select(Song)
            .where(
                or_(
                    Song.artist.ilike(pattern),
                    Song.album.ilike(pattern),
                    Song.title.ilike(pattern),
                    Song.path.ilike(pattern),
                    Song.genre.ilike(pattern),
                )
            )
            .order_by(Song.artist, Song.album, Song.track_number)
        ).scalars().all()
        return list(result)


def get_song(song_id: int) -> Song | None:
    with session_scope() as session:
        return session.get(Song, song_id)


def delete_song(song_id: int) -> bool:
    with session_scope() as session:
        song = session.get(Song, song_id)
        if song is None:
            return False
        session.delete(song)
        return True


def update_song_tags(song_id: int, tag: tagmod.TagInfo, *, write_to_file: bool = True) -> bool:
    with session_scope() as session:
        song = session.get(Song, song_id)
        if song is None:
            return False
        song.title = tag.title
        song.artist = tag.artist
        song.album = tag.album
        song.year = tag.year
        song.genre = tag.genre
        song.track_number = tag.track_number
        if write_to_file:
            tagmod.write_tags(song.path, tag)
        return True


def mark_played(song_id: int) -> None:
    with session_scope() as session:
        song = session.get(Song, song_id)
        if song is None:
            return
        song.play_count = (song.play_count or 0) + 1
        song.last_played_at = _dt.datetime.utcnow()


def remove_missing_files() -> int:
    """Delete library rows whose file no longer exists on disk."""
    removed = 0
    with session_scope() as session:
        for song in session.execute(select(Song)).scalars():
            if not Path(song.path).exists():
                session.delete(song)
                removed += 1
    return removed


def stats() -> dict[str, int | float]:
    with session_scope() as session:
        total_songs = session.scalar(select(func.count(Song.id))) or 0
        total_artists = session.scalar(
            select(func.count(func.distinct(Song.artist)))
        ) or 0
        total_albums = session.scalar(
            select(func.count(func.distinct(Song.album)))
        ) or 0
        total_duration = session.scalar(select(func.coalesce(func.sum(Song.duration), 0.0))) or 0.0
        total_radios = session.scalar(select(func.count(Radio.id))) or 0
    return {
        "songs": int(total_songs),
        "artists": int(total_artists),
        "albums": int(total_albums),
        "duration": float(total_duration),
        "radios": int(total_radios),
    }


# ---------------------------------------------------------------------------
# Radios
# ---------------------------------------------------------------------------


def fetch_radios() -> list[Radio]:
    with session_scope() as session:
        return list(session.execute(select(Radio).order_by(Radio.name, Radio.url)).scalars())


def add_radio(url: str, name: str = "", genre: str = "", bitrate: str = "") -> Radio:
    if not url.strip():
        raise ValueError("radio URL is required")
    with session_scope() as session:
        radio = Radio(url=url.strip(), name=name.strip(), genre=genre.strip(), bitrate=bitrate.strip())
        session.add(radio)
        session.flush()
        session.refresh(radio)
        return radio


def delete_radio(radio_id: int) -> bool:
    with session_scope() as session:
        radio = session.get(Radio, radio_id)
        if radio is None:
            return False
        session.delete(radio)
        return True


# ---------------------------------------------------------------------------
# Playlists
# ---------------------------------------------------------------------------


def create_playlist(name: str, song_ids: Iterable[int] = ()) -> Playlist:
    name = name.strip()
    if not name:
        raise ValueError("playlist name is required")
    with session_scope() as session:
        playlist = Playlist(name=name, created_at=_dt.datetime.utcnow())
        session.add(playlist)
        session.flush()
        for pos, sid in enumerate(song_ids):
            session.add(PlaylistItem(playlist_id=playlist.id, song_id=sid, position=pos))
        session.flush()
        session.refresh(playlist)
        return playlist


def list_playlists() -> list[Playlist]:
    with session_scope() as session:
        return list(session.execute(select(Playlist).order_by(Playlist.name)).scalars())


def get_playlist_songs(playlist_id: int) -> list[Song]:
    with session_scope() as session:
        items = session.execute(
            select(PlaylistItem).where(PlaylistItem.playlist_id == playlist_id).order_by(PlaylistItem.position)
        ).scalars()
        out: list[Song] = []
        for item in items:
            song = session.get(Song, item.song_id)
            if song is not None:
                out.append(song)
        return out


def delete_playlist(playlist_id: int) -> bool:
    with session_scope() as session:
        pl = session.get(Playlist, playlist_id)
        if pl is None:
            return False
        session.delete(pl)
        return True


def add_to_playlist(playlist_id: int, song_id: int) -> None:
    with session_scope() as session:
        max_pos = session.scalar(
            select(func.coalesce(func.max(PlaylistItem.position), -1)).where(
                PlaylistItem.playlist_id == playlist_id
            )
        )
        session.add(PlaylistItem(playlist_id=playlist_id, song_id=song_id, position=(max_pos or -1) + 1))


def clear_playlist(playlist_id: int) -> None:
    with session_scope() as session:
        session.execute(delete(PlaylistItem).where(PlaylistItem.playlist_id == playlist_id))


# ---------------------------------------------------------------------------
# Playlist generator (legacy `gen_list`): copy filtered songs into a folder
# up to a maximum size.
# ---------------------------------------------------------------------------


@dataclass
class GenerateResult:
    copied: int = 0
    skipped: int = 0
    total_bytes: int = 0
    errors: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []


def generate_playlist_to_dir(
    *,
    filter_query: str,
    destination: str | Path,
    max_size_mb: int,
    on_progress: Optional[callable] = None,  # type: ignore[type-arg]
) -> GenerateResult:
    """Copy songs matching *filter_query* into *destination* up to *max_size_mb*.

    Replaces ``MainWindow.list_generator`` from the legacy GUI.
    """
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)
    budget = int(max_size_mb) * 1024 * 1024
    songs = search_songs(filter_query)
    result = GenerateResult()

    for song in songs:
        src = Path(song.path)
        try:
            size = src.stat().st_size
        except OSError as exc:
            result.errors.append(f"{src}: {exc}")
            result.skipped += 1
            continue
        if result.total_bytes + size > budget:
            break
        try:
            shutil.copy2(src, dest / src.name)
        except OSError as exc:
            result.errors.append(f"{src}: {exc}")
            result.skipped += 1
            continue
        result.copied += 1
        result.total_bytes += size
        if on_progress is not None:
            on_progress(result)
    return result
