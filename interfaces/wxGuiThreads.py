import threading
import wx

class ShowPosThread(threading.Thread):

    def __init__(self, clock, player, id):
        threading.Thread.__init__(self)
        self.clock = clock
        self.player = player
        self.id = id
        self.mutex = threading.Lock()

    def run(self):

        while (self.player.isPlaying() or self.player.isPaused()) and self.id == self.player.id:

            wx.MutexGuiEnter()

            time = self.player.getPosition()
            if time:
                self.clock.SetValue(time)

            wx.MutexGuiLeave()


    def __del__(self):
        del(self)
