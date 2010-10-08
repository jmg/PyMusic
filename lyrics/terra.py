import urllib2
from utils import EspecialChars

class LyricsTerra(object):

    BASE_URL = 'http://letras.terra.com.br/winamp.php?t=%s-%s'

    def __init__(self, song, artist):
        song = song.replace(" ", "%20")
        artist = artist.replace(" ", "%20")

        self.url = self.BASE_URL % (artist, song)
        self.source = urllib2.urlopen(self.url).read()

    def parse_lyrics(self):
        self.source = re.split('<div id="letra">', self.source)[1]
        self.source = re.split('<p>', self.source)
        # Parse artist and title
        artistitle = re.sub('<.*?>', '', self.source[0])
        # Parse lyrics
        lyrics = re.split('</p>', self.source[1])[0]
        lyrics = re.sub('<[Bb][Rr]/>', '', lyrics)

        lyrics = EspecialChars.unescape_entities(lyrics)

        return lyrics


if __name__ == "__main__":

    artist = 'pet%20shop%20boys'
    song = 'footsteps'

    lyrics = LyricsTerra(song, artist)
    print lyrics.parse_lyrics()

