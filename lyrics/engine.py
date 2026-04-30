import queue

from generics.multiprogramming import threaded
from lyrics.terra import LyricsTerra

_results = queue.Queue()


@threaded
def worker(Resource, song, artist):
    lyrics = Resource(song, artist)
    _results.put(lyrics.parse_lyrics())


class LyricsSearcher:

    resources = [LyricsTerra]

    def __init__(self, song, artist):
        self.song = song
        self.artist = artist

    def get_lyrics(self):
        for resource in self.resources:
            worker(resource, self.song, self.artist)
        return _results.get()
