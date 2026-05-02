import os
import time

try:
    from mutagen import File as _MutagenFile
except ImportError:
    _MutagenFile = None

from logic.tags import Tags

validFormats = [
    '.mp3', '.flac', '.ogg', '.oga', '.opus', '.m4a', '.aac', '.wav',
    '.wma', '.ape', '.alac', '.aiff', '.aif', '.dsf', '.dff', '.mpc',
    '.wv',
]


def list_dir(root):
    """Recursively list audio files inside ``root``."""
    listSongs = []

    for current_root, _sub_folders, files in os.walk(root):
        for file in files:
            if isValidFormat(file):
                path = os.path.join(current_root, file)
                listSongs.append(_song_record(path))

    return listSongs


def list_files(paths):
    """Build song records for an explicit list of file paths."""
    return [_song_record(p) for p in paths if isValidFormat(p)]


def _song_record(path):
    """Return [id, path, artist, album, year, title, duration, play_count,
    added_at, last_played] matching Song(...) __init__ order."""
    t = Tags(path)
    duration = _read_duration(path)
    return [
        None,                  # id
        path,
        t.artista(),
        t.album(),
        t.year(),
        t.titulo(),
        duration,
        0,                     # play_count
        int(time.time()),      # added_at
        None,                  # last_played
    ]


def _read_duration(path):
    if not _MutagenFile:
        return None
    try:
        audio = _MutagenFile(path)
        if audio is not None and getattr(audio, 'info', None):
            return int(audio.info.length)
    except Exception:
        pass
    return None


def isValidFormat(name):
    name = name.lower()
    return any(name.endswith(fmt) for fmt in validFormats)
