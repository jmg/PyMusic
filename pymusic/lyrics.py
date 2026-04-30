"""Lyrics fetching with on-disk caching.

The original ``lyrics/terra.py`` scraped ``letras.terra.com.br``, which
is no longer reachable / maintained. We use the lyrics.ovh public API,
which is keyless, JSON-only, and CORS-friendly. Results are cached on
disk so a second lookup never hits the network.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover - requests is required
    requests = None  # type: ignore[assignment]

from .config import get_settings

logger = logging.getLogger(__name__)

_API_URL = "https://api.lyrics.ovh/v1/{artist}/{title}"
_TIMEOUT = 6.0


class LyricsError(RuntimeError):
    pass


def _cache_path(artist: str, title: str) -> Path:
    key = f"{artist.strip().lower()}|{title.strip().lower()}".encode()
    digest = hashlib.sha1(key).hexdigest()
    return get_settings().lyrics_cache_dir / f"{digest}.txt"


def get_lyrics(artist: str, title: str, *, use_cache: bool = True) -> str:
    """Return lyrics text for *artist* / *title*. Empty string if unknown.

    Network and parse errors are logged and turned into an empty result —
    the GUI should never crash because lyrics are unavailable.
    """
    if not (artist or title):
        return ""

    cache = _cache_path(artist, title)
    if use_cache and cache.exists():
        try:
            return cache.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("could not read lyrics cache %s: %s", cache, exc)

    if requests is None:
        return ""

    url = _API_URL.format(artist=requests.utils.quote(artist or ""),
                          title=requests.utils.quote(title or ""))
    try:
        resp = requests.get(url, timeout=_TIMEOUT)
        if resp.status_code == 404:
            text = ""
        else:
            resp.raise_for_status()
            data = resp.json()
            text = (data.get("lyrics") or "").strip()
    except (requests.RequestException, ValueError) as exc:  # type: ignore[union-attr]
        logger.info("lyrics fetch failed for %r/%r: %s", artist, title, exc)
        return ""

    if text:
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(text, encoding="utf-8")
        except OSError as exc:
            logger.warning("could not write lyrics cache %s: %s", cache, exc)
    return text
