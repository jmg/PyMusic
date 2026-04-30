import os
import threading
import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib  # noqa: F401  (kept available for callers)


class ShowPosThread(threading.Thread):

    def __init__(self, clock, entry, song, player, id):
        threading.Thread.__init__(self)
        self.daemon = True
        self.clock = clock
        self.player = player
        self.entry = entry
        self.song = song
        self.id = id

    def run(self):
        while (self.player.isPlaying() or self.player.isPaused()) and self.id == self.player.id:
            position = self.player.getPosition()
            if position:
                GLib.idle_add(self.clock.set_text, position)
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

        if not duration or duration == -1:
            return

        adjust = self.bar.get_adjustment()
        GLib.idle_add(self.bar.set_range, 0, duration)

        while (self.player.isPlaying() or self.player.isPaused()) and self.id == self.player.id:
            pos = self.player.getSeekedPosition()
            if pos:
                GLib.idle_add(adjust.set_value, pos)
            time.sleep(0.5)


class RandomListThread(threading.Thread):

    def __init__(self, songs, size, path):
        threading.Thread.__init__(self)
        self.daemon = True
        self.size = size
        self.songs = songs
        self.path = path

    def run(self):
        self.size *= 1024  # bytes to kilo
        self.size *= 1024  # kilo to mega
        acum = 0
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        for song in self.songs:
            try:
                filesize = os.path.getsize(song[0])
            except OSError:
                continue
            acum += filesize
            if self.size <= acum:
                break
            command = f'cp "{song[0]}" "{self.path}"'
            print(command)
            try:
                os.system(command)
            except Exception:
                acum -= filesize
                continue
