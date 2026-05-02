from lyrics.lrclib import LyricsLRCLIB, parse_lrc


class LyricsSearcher:

    resources = [LyricsLRCLIB]

    def __init__(self, song, artist):
        self.song = song
        self.artist = artist
        self._synced_cache = None

    def get_lyrics(self):
        for resource in self.resources:
            try:
                obj = resource(self.song, self.artist)
                text = obj.parse_lyrics()
                if text and text != "No se encontraron letras":
                    if hasattr(obj, "parse_synced"):
                        try:
                            self._synced_cache = obj.parse_synced()
                        except Exception:
                            self._synced_cache = None
                    return text
            except Exception:
                continue
        return "No se encontraron letras"

    def get_synced(self):
        """Return parsed [(seconds, line), ...] or [] if no synced lyrics."""
        return parse_lrc(self._synced_cache) if self._synced_cache else []
