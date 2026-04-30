import re
from urllib.request import urlopen

from lyrics.utils import EspecialChars


class LyricsTerra:

    BASE_URL = 'http://letras.terra.com.br/winamp.php?t=%s-%s'

    def __init__(self, song, artist):
        song = song.replace(" ", "%20")
        artist = artist.replace(" ", "%20")
        self.url = self.BASE_URL % (artist, song)

    def parse_lyrics(self):
        try:
            with urlopen(self.url) as response:
                source = response.read().decode('utf-8', errors='replace')
            source = re.split('<div id="letra">', source)[1]
            parts = re.split('<p>', source)
            # Parse lyrics
            lyrics = re.split('</p>', parts[1])[0]
            lyrics = re.sub('<[Bb][Rr]/>', '', lyrics)
            lyrics = EspecialChars.unescape_entities(lyrics)
        except Exception as e:
            print(e)
            lyrics = "No se encontraron letras"

        return lyrics


if __name__ == "__main__":
    artist = 'creedence'
    song = 'proud mary'

    lyrics = LyricsTerra(song, artist)
    print(lyrics.parse_lyrics())
