import urllib2
import re
from utils import EspecialChars

class LyricsTerra(object):

    BASE_URL = 'http://letras.terra.com.br/winamp.php?t=%s-%s'

    def __init__(self, song, artist):
        song = song.replace(" ", "%20")
        artist = artist.replace(" ", "%20")

        self.url = self.BASE_URL % (artist, song)

    def parse_lyrics(self):
        try:
            source = urllib2.urlopen(self.url).read()
            source = re.split('<div id="letra">', source)[1]
            source = re.split('<p>', source)
            # Parse artist and title
            artistitle = re.sub('<.*?>', '', source[0])
            # Parse lyrics
            lyrics = re.split('</p>', source[1])[0]
            lyrics = re.sub('<[Bb][Rr]/>', '', lyrics)

            lyrics = EspecialChars.unescape_entities(lyrics)
        except Exception, e:
            print e.message
            lyrics = "No se encontraron letras"

        return lyrics


if __name__ == "__main__":

    artist = 'creedence'
    song = 'proud mary'

    lyrics = LyricsTerra(song, artist)
    print lyrics.parse_lyrics()

