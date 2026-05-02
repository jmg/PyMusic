# -*- coding: utf-8 -*-
"""Audio tag reader.

Uses mutagen for ID3v2 and other modern tag formats; falls back to
ID3v1 (legacy implementation) when mutagen isn't available.
"""

try:
    from mutagen import File as MutagenFile
    _MUTAGEN = True
except ImportError:
    MutagenFile = None
    _MUTAGEN = False


class Tags:

    def __init__(self, mp3):
        self.mp3 = mp3
        self._title = None
        self._artist = None
        self._album = None
        self._year = None
        self._cover = None

        if _MUTAGEN:
            self._read_mutagen()
        if self._artist is None:
            self._read_id3v1()

    def _read_mutagen(self):
        try:
            audio = MutagenFile(self.mp3)
        except Exception:
            return
        if audio is None:
            return

        def first(*keys):
            for k in keys:
                v = audio.get(k)
                if v:
                    if isinstance(v, list):
                        v = v[0]
                    s = str(v).strip()
                    if s:
                        return s
            return None

        # Try common ID3 (TIT2/TPE1/...) and easy tags first.
        tags = {}
        try:
            tags = dict(audio.tags) if audio.tags else {}
        except Exception:
            pass

        self._title = first('TIT2', 'title', '\xa9nam')
        self._artist = first('TPE1', 'artist', '\xa9ART')
        self._album = first('TALB', 'album', '\xa9alb')
        year = first('TDRC', 'date', 'year', '\xa9day')
        if year:
            self._year = year[:4]

        # Embedded cover art
        try:
            for k in tags:
                key = str(k)
                if key.startswith('APIC'):
                    self._cover = tags[k].data
                    return
            covr = tags.get('covr')
            if covr:
                self._cover = bytes(covr[0])
                return
            pictures = getattr(audio, 'pictures', None)
            if pictures:
                self._cover = pictures[0].data
        except Exception:
            pass

    def _read_id3v1(self):
        try:
            with open(self.mp3, 'rb') as f:
                f.seek(-128, 2)
                data = f.read()
        except (OSError, ValueError):
            return

        def decode(raw):
            return raw.replace(b'\x00', b'').decode('utf-8', errors='replace').strip()

        try:
            if data[0:3] == b'TAG':
                t = self.isValid(decode(data[3:33]))
                a = self.isValid(decode(data[33:63]))
                al = self.isValid(decode(data[63:93]))
                y = self.isValidYear(decode(data[93:97]))
                if self._title is None:
                    self._title = t
                if self._artist is None:
                    self._artist = a
                if self._album is None:
                    self._album = al
                if self._year is None:
                    self._year = y
        except Exception:
            pass

    def titulo(self):
        return self._title or "Desconocido"

    def artista(self):
        return self._artist or "Desconocido"

    def album(self):
        return self._album or "Desconocido"

    def year(self):
        return self._year or "-"

    def cover(self):
        """Return raw image bytes or None."""
        return self._cover

    def replaygain(self):
        """Return ReplayGain track gain in dB (float) or None."""
        if not _MUTAGEN:
            return None
        try:
            audio = MutagenFile(self.mp3, easy=False)
        except Exception:
            return None
        if audio is None:
            return None
        try:
            tags = audio.tags or {}
        except Exception:
            tags = {}

        # ID3v2: TXXX:replaygain_track_gain
        for key, val in dict(tags).items():
            sk = str(key).lower()
            if "replaygain_track_gain" in sk:
                if hasattr(val, "text"):
                    val = val.text
                if isinstance(val, list):
                    val = val[0]
                return self._parse_db(str(val))
        # Vorbis / FLAC easy keys
        for k in ("replaygain_track_gain",):
            v = audio.get(k) if hasattr(audio, "get") else None
            if v:
                if isinstance(v, list):
                    v = v[0]
                return self._parse_db(str(v))
        return None

    @staticmethod
    def _parse_db(s):
        s = s.strip().split()[0].rstrip("dB").strip()
        try:
            return float(s)
        except ValueError:
            return None

    def isValid(self, string):
        if not string or string.isspace() or string.count("U") > 3:
            return None
        return string

    def isValidYear(self, string):
        if not string or string.isspace() or string.count("U") > 3:
            return None
        return string

    def list(self):
        return [self.artista(), self.album(), self.year()]
