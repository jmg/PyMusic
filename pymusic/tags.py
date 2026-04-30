"""Audio metadata via mutagen.

Provides a single :class:`TagInfo` dataclass and helpers to read and
write tags for any format mutagen supports, with safe fallbacks if a
file has no tags or is corrupt.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from mutagen import File as MutagenFile
    from mutagen import MutagenError
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3NoHeaderError
except ImportError:  # pragma: no cover - mutagen is required
    MutagenFile = None  # type: ignore[assignment]
    EasyID3 = None  # type: ignore[assignment]
    ID3NoHeaderError = Exception  # type: ignore[assignment, misc]
    MutagenError = Exception  # type: ignore[assignment, misc]


@dataclass
class TagInfo:
    title: str = ""
    artist: str = ""
    album: str = ""
    year: str = ""
    genre: str = ""
    track_number: int = 0
    duration: float = 0.0  # seconds

    def as_dict(self) -> dict:
        return asdict(self)


def _first(values) -> str:
    if not values:
        return ""
    if isinstance(values, (list, tuple)):
        return str(values[0]) if values else ""
    return str(values)


def _parse_track_number(raw: str) -> int:
    if not raw:
        return 0
    raw = raw.split("/", 1)[0]
    try:
        return int(raw)
    except ValueError:
        return 0


def read_tags(path: str | Path) -> TagInfo:
    """Read tags from an audio file. Always returns a :class:`TagInfo`.

    Missing tags are returned as empty strings / zero. The file's stem is
    used as a fallback title.
    """
    p = Path(path)
    info = TagInfo(title=p.stem)

    if MutagenFile is None:
        return info

    try:
        audio = MutagenFile(p, easy=True)
    except (OSError, MutagenError):
        return info
    if audio is None:
        return info

    info.title = _first(audio.get("title")) or p.stem
    info.artist = _first(audio.get("artist"))
    info.album = _first(audio.get("album"))
    info.year = _first(audio.get("date") or audio.get("year"))
    info.genre = _first(audio.get("genre"))
    info.track_number = _parse_track_number(_first(audio.get("tracknumber")))

    if hasattr(audio, "info") and getattr(audio.info, "length", None):
        info.duration = float(audio.info.length)

    return info


def write_tags(path: str | Path, tags: TagInfo) -> bool:
    """Write tags back to disk. Returns True on success."""
    if MutagenFile is None:
        return False
    p = Path(path)
    try:
        audio = MutagenFile(p, easy=True)
        if audio is None:
            return False
        if audio.tags is None:
            audio.add_tags()
        audio["title"] = tags.title or p.stem
        audio["artist"] = tags.artist
        audio["album"] = tags.album
        if tags.year:
            audio["date"] = tags.year
        if tags.genre:
            audio["genre"] = tags.genre
        if tags.track_number:
            audio["tracknumber"] = str(tags.track_number)
        audio.save()
        return True
    except (OSError, MutagenError, KeyError, ValueError):
        return False


def format_duration(seconds: float) -> str:
    """Format a duration as ``mm:ss`` or ``h:mm:ss``."""
    if seconds <= 0:
        return "0:00"
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
