from pynotify import Notification

class SongNotify(Notification):

    def __init__(self, song):

        Notification.__init__(self, song)
        self.show()

