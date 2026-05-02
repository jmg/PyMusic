"""MusicBrainz / Cover Art Archive lookup with on-disk caching.

Used as a fallback when an audio file has no embedded cover art.
"""

import hashlib
import json
import os
from urllib.parse import quote
from urllib.request import Request, urlopen


CACHE_DIR = os.path.expanduser("~/.cache/pymusic/covers")
UA = "PyMusic/1.0 ( https://example.com/pymusic )"


def _http_json(url, timeout=3):
    req = Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _http_bytes(url, timeout=5):
    req = Request(url, headers={"User-Agent": UA})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _cache_key(artist, album):
    h = hashlib.sha1(f"{artist}::{album}".lower().encode("utf-8")).hexdigest()
    return os.path.join(CACHE_DIR, f"{h}.bin")


def fetch_cover(artist, album):
    """Return raw cover image bytes for an artist+album, or None."""
    if not artist or not album:
        return None

    cache_path = _cache_key(artist, album)
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "rb") as f:
                return f.read() or None
        except OSError:
            pass

    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
    except OSError:
        pass

    try:
        # 1) Find a release-group that matches.
        q = f'release:"{album}" AND artist:"{artist}"'
        url = f"https://musicbrainz.org/ws/2/release-group/?query={quote(q)}&fmt=json&limit=3"
        data = _http_json(url)
        groups = data.get("release-groups") or []
        for g in groups:
            mbid = g.get("id")
            if not mbid:
                continue
            # 2) Try Cover Art Archive front cover.
            cover_url = f"https://coverartarchive.org/release-group/{mbid}/front-500"
            try:
                blob = _http_bytes(cover_url)
                if blob:
                    try:
                        with open(cache_path, "wb") as f:
                            f.write(blob)
                    except OSError:
                        pass
                    return blob
            except Exception:
                continue
    except Exception:
        pass

    # Negative cache: write empty file so we don't retry every play.
    try:
        with open(cache_path, "wb") as f:
            f.write(b"")
    except OSError:
        pass
    return None
