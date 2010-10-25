import threading
import wx

class ShowPosThread(threading.Thread):

    def __init__(self, clock, player, id):
        threading.Thread.__init__(self)
        self.clock = clock
        self.player = player
        self.id = id

    def run(self):

        while (self.player.isPlaying() or self.player.isPaused()) and self.id == self.player.id:

            wx.MutexGuiEnter()

            time = self.player.getPosition()
            if time:
                self.clock.SetValue(time)

            wx.MutexGuiLeave()

    def __del__(self):
        del(self)


class MoveBarThread(threading.Thread):

    def __init__(self, bar, player, id):
        threading.Thread.__init__(self)
        self.bar = bar
        self.player = player
        self.id = id

    def run(self):
        duration = None
        while not duration:
            try:
                duration = self.player.getSeekableDuration()
            except:
                pass

        if duration != -1:
            self.bar.SetRange(0, duration/1000)
        else:
            try:
                self.adjust.value = 0
            except:
                pass
            return

        while (self.player.isPlaying() or self.player.isPaused()) and self.id == self.player.id:
            wx.MutexGuiEnter()

            pos = self.player.getSeekedPosition()
            if pos:
                self.bar.SetValue(pos/1000)

            wx.MutexGuiLeave()

    def __del__(self):
        del(self)
