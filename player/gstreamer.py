# -*- coding: utf-8 -*-
import gst
import os
import gtk
import threading
import time

gtk.gdk.threads_init()

class mp3player:

    def __init__(self):
        self.player = gst.element_factory_make("playbin", "player")
        self.timeFormat = gst.Format(gst.FORMAT_TIME)

    def play(self, path, next=None, id=None):
        self.next = next
        self.id = id

        uri = self.getUri(path)

        self.player.set_property('uri', uri)
        try:
            self.player.set_state(gst.STATE_PLAYING)
        except:
            pass
        bus = self.player.get_bus()
        bus.add_watch(self.eventListener)

    def playList(self, listSongs):
        for song in listSongs:
            self.play(song, None, None)

    def getUri(self, path):
        if path.find("http://") != -1 or path.find("file://") != -1:
            return path
        return "file://" + path

    def stop(self):
        if self.isPlaying():
            self.player.set_state(gst.STATE_NULL)

    def resume(self):
        if not self.isPlaying():
            self.player.set_state(gst.STATE_PLAYING)

    def pause(self):
        if self.isPlaying():
            self.player.set_state(gst.STATE_PAUSED)

    def getPosition(self):
        if self.isPlaying():
            pos = None
            while not pos:
                try:
                    pos = self.player.query_position(self.timeFormat, None)[0]
                except:
                    pass
            return self.convertTime(pos)

    def getSeekedPosition(self):
        if self.isPlaying():
            pos = None
            while not pos:
                try:
                    pos = self.player.query_position(self.timeFormat, None)[0]
                except:
                    pass
            return pos

    def getSeekableDuration(self):
        return self.player.query_duration(gst.FORMAT_TIME, None)[0]

    def seek(self, position):
        self.player.seek(1.0, gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH, gst.SEEK_TYPE_SET, position, gst.SEEK_TYPE_NONE,0)

    def change_volume(self, volume):
        self.player.set_property("volume",volume)

    def isPlaying(self):
        self.state = self.player.get_state()[1]
        if self.state.value_nick == 'playing':
            return True
        return False

    def isPaused(self):
        self.state = self.player.get_state()[1]
        if self.state.value_nick == 'paused':
            return True
        return False

    def eventListener(self, bus, event):
        if event.type == gst.MESSAGE_EOS:
            self.next()
        return True

    #solucion no optima
    def songFinished(self):
        pos = self.getPosition()
        time.sleep(2)
        newPos = self.getPosition()
        if pos == newPos:
            return True
        return False

    def convertTime(self, time):
        time_int = time / 1000000000
        mins = time_int / 60
        segs = time_int % 60
        if mins < 10:
            mins = "0" + str(mins)
        else:
            mins = str(mins)

        if segs < 10:
            segs = "0" + str(segs)
        else:
            segs = str(segs)

#        milisegs = (time / 1000000) % 1000
#        if milisegs < 100:
#            milisegs = "0" + str(milisegs)
#        elif milisegs < 10:
#            milisegs = "00" + str(milisegs)
#        else:
#            milisegs = str(milisegs)

        return mins + ":" + segs #+ "." + milisegs







