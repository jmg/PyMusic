import Queue
from terra import LyricsTerra
from generics.multiprogramming import threaded

queue = Queue.Queue()

@threaded
def worker(Resource, song, artist):

    lyrics = Resource(song, artist)
    queue.put(lyrics.parse_lyrics())


class LyricsSearcher(object):

    resources = [LyricsTerra, ]

    def __init__(self, song, artist):
        self.song = song
        self.artist = artist

    def get_lyrics(self):
        for resource in self.resources:
            worker(resource, self.song, self.artist)
        return queue.get()
