"""LRCLIB-backed lyrics fetcher.

LRCLIB (https://lrclib.net) is an open lyrics database with both plain
and synced (LRC) formats. No API key required.
"""

import json
import re
from urllib.parse import quote
from urllib.request import Request, urlopen


class LyricsLRCLIB:

    BASE = "https://lrclib.net/api/get?artist_name={a}&track_name={t}"
    SEARCH = "https://lrclib.net/api/search?q={q}"
    UA = "PyMusic/1.0 (https://example.com)"

    def __init__(self, song, artist):
        self.song = song or ""
        self.artist = artist or ""

    def _http_get(self, url):
        req = Request(url, headers={"User-Agent": self.UA})
        with urlopen(req, timeout=2) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))

    def parse_lyrics(self):
        """Return plain text lyrics (synced timestamps stripped)."""
        synced, plain = self._fetch()
        if synced:
            return self._strip_timestamps(synced)
        return plain or "No se encontraron letras"

    def parse_synced(self):
        """Return raw LRC text (with [mm:ss.xx] timestamps) or None."""
        synced, _ = self._fetch()
        return synced

    def _fetch(self):
        try:
            url = self.BASE.format(
                a=quote(self.artist), t=quote(self.song),
            )
            data = self._http_get(url)
            if isinstance(data, dict) and (data.get("syncedLyrics") or data.get("plainLyrics")):
                return data.get("syncedLyrics"), data.get("plainLyrics")
        except Exception:
            pass

        # Fall back to free-text search
        try:
            q = f"{self.artist} {self.song}".strip()
            if not q:
                return None, None
            results = self._http_get(self.SEARCH.format(q=quote(q)))
            if isinstance(results, list) and results:
                top = results[0]
                return top.get("syncedLyrics"), top.get("plainLyrics")
        except Exception:
            pass

        return None, None

    @staticmethod
    def _strip_timestamps(lrc):
        return re.sub(r"\[\d{1,2}:\d{2}(?:\.\d{1,3})?\]", "", lrc).strip()


def parse_lrc(lrc_text):
    """Parse an LRC string into a sorted list of (seconds, line) tuples."""
    out = []
    if not lrc_text:
        return out
    pattern = re.compile(r"\[(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?\]")
    for raw in lrc_text.splitlines():
        timestamps = pattern.findall(raw)
        text = pattern.sub("", raw).strip()
        for mm, ss, ms in timestamps:
            t = int(mm) * 60 + int(ss) + (int(ms.ljust(3, "0")) / 1000.0 if ms else 0)
            out.append((t, text))
    out.sort(key=lambda x: x[0])
    return out
