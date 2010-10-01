import threading
import gtk

class ShowPosThread(threading.Thread):

    def __init__(self, clock, entry, song, player, id):
        threading.Thread.__init__(self)
        self.clock = clock
        self.player = player
        self.entry = entry
        self.song = song
        self.id = id
        self.mutex = threading.Lock()

    def run(self):

        while (self.player.isPlaying() or self.player.isPaused()) and self.id == self.player.id:
            self.mutex.acquire()
            gtk.gdk.threads_enter()
            time = self.player.getPosition()
            if time:
                self.clock.set_text(time)

            gtk.gdk.threads_leave()
            self.mutex.release()


    def __del__(self):
        del(self)


class MoveBarThread(threading.Thread):

    def __init__(self, bar, player, id):
        threading.Thread.__init__(self)
        self.bar = bar
        self.player = player
        self.id = id

        self.adjust = self.bar.get_adjustment()
        self.mutex = threading.Lock()

    def run(self):
        duration = None
        while not duration:
            try:
                duration = self.player.getSeekableDuration()
            except:
                pass

        if duration != -1:
            self.bar.set_range(0, duration)
        else:
            try:
                self.adjust.value = 0
            except:
                pass
            return

        while (self.player.isPlaying() or self.player.isPaused()) and self.id == self.player.id:
            self.mutex.acquire()
            gtk.gdk.threads_enter()
            pos = self.player.getSeekedPosition()
            if pos:
                self.adjust.value = pos
                self.adjust.emit("changed")

            gtk.gdk.threads_leave()
            self.mutex.release()

    def __del__(self):
        del(self)


class RandomListThread(threading.Thread):

    def __init__(self, songs, size, path):
        gstreamer.threading.Thread.__init__(self)
        self.size = size
        self.songs = songs
        self.path = path

    def run(self):
        self.size *= 1024 #bytes to kilo
        self.size *= 1024 #kilo to mega
        #self.size *= 1024 #mega to giga
        acum = 0
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        for song in self.songs:
            try:
                filesize = os.path.getsize(song[0])
            except:
                continue
            acum += filesize
            if self.size <= acum:
                break
            command = 'cp "'+ song[0] + '" "' + self.path + '"'
            print command
            try:
                os.system(command)
            except:
                acum -= filesize
                continue

