import threading
import time

import wx


class ShowPosThread(threading.Thread):

    def __init__(self, clock, player, id):
        threading.Thread.__init__(self)
        self.daemon = True
        self.clock = clock
        self.player = player
        self.id = id

    def run(self):
        while (self.player.isPlaying() or self.player.isPaused()) and self.id == self.player.id:
            position = self.player.getPosition()
            if position:
                wx.CallAfter(self.clock.SetValue, position)
            time.sleep(0.5)


class MoveBarThread(threading.Thread):

    def __init__(self, bar, player, id):
        threading.Thread.__init__(self)
        self.daemon = True
        self.bar = bar
        self.player = player
        self.id = id

    def run(self):
        duration = None
        for _ in range(50):
            try:
                duration = self.player.getSeekableDuration()
                if duration:
                    break
            except Exception:
                pass
            time.sleep(0.1)

        if duration is None or duration == -1:
            return

        wx.CallAfter(self.bar.SetRange, 0, duration // 1000)

        while (self.player.isPlaying() or self.player.isPaused()) and self.id == self.player.id:
            pos = self.player.getSeekedPosition()
            if pos:
                wx.CallAfter(self.bar.SetValue, pos // 1000)
            time.sleep(0.5)
