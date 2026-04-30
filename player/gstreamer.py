# -*- coding: utf-8 -*-
"""GStreamer 1.0 backed mp3 player via PyGObject.

Falls back to a no-op stub when GStreamer is unavailable so that the rest of
the application can still be imported (useful in headless test/CI envs).
"""

import time

try:
    import gi
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst

    Gst.init(None)
    _GST_AVAILABLE = True
except (ImportError, ValueError):
    Gst = None
    _GST_AVAILABLE = False


class mp3player:

    def __init__(self):
        if _GST_AVAILABLE:
            self.player = Gst.ElementFactory.make("playbin", "player")
        else:
            self.player = None
        self.next = None
        self.id = None

    # ------------------------------------------------------------------
    # Playback control
    # ------------------------------------------------------------------
    def play(self, path, next=None, id=None):
        self.next = next
        self.id = id
        if not self.player:
            return

        self.player.set_property('uri', self.getUri(path))
        try:
            self.player.set_state(Gst.State.PLAYING)
        except Exception:
            pass

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self._on_bus_message)

    def playList(self, listSongs):
        for song in listSongs:
            self.play(song, None, None)

    def getUri(self, path):
        if path.find("http://") != -1 or path.find("file://") != -1:
            return path
        return "file://" + path

    def stop(self):
        if self.isPlaying() and self.player:
            self.player.set_state(Gst.State.NULL)

    def resume(self):
        if not self.isPlaying() and self.player:
            self.player.set_state(Gst.State.PLAYING)

    def pause(self):
        if self.isPlaying() and self.player:
            self.player.set_state(Gst.State.PAUSED)

    def change_volume(self, volume):
        if self.player:
            self.player.set_property("volume", volume)

    # ------------------------------------------------------------------
    # Position queries
    # ------------------------------------------------------------------
    def getPosition(self):
        if not (self.isPlaying() and self.player):
            return None
        pos = self._query_position()
        if pos is None:
            return None
        return self.convertTime(pos)

    def getSeekedPosition(self):
        if not (self.isPlaying() and self.player):
            return None
        return self._query_position()

    def _query_position(self):
        for _ in range(10):
            ok, pos = self.player.query_position(Gst.Format.TIME)
            if ok:
                return pos
        return None

    def getSeekableDuration(self):
        if not self.player:
            return -1
        ok, dur = self.player.query_duration(Gst.Format.TIME)
        return dur if ok else -1

    def seek(self, position):
        if not self.player:
            return
        self.player.seek(
            1.0,
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH,
            Gst.SeekType.SET, position,
            Gst.SeekType.NONE, 0,
        )

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------
    def isPlaying(self):
        if not self.player:
            return False
        _, state, _ = self.player.get_state(Gst.CLOCK_TIME_NONE)
        return state == Gst.State.PLAYING

    def isPaused(self):
        if not self.player:
            return False
        _, state, _ = self.player.get_state(Gst.CLOCK_TIME_NONE)
        return state == Gst.State.PAUSED

    # ------------------------------------------------------------------
    # Bus events
    # ------------------------------------------------------------------
    def _on_bus_message(self, bus, message):
        if message.type == Gst.MessageType.EOS and self.next:
            self.next()

    # solucion no optima
    def songFinished(self):
        pos = self.getPosition()
        time.sleep(2)
        newPos = self.getPosition()
        return pos == newPos

    def convertTime(self, ns_time):
        time_int = ns_time // 1_000_000_000
        mins = time_int // 60
        segs = time_int % 60
        mins_s = f"{mins:02d}"
        segs_s = f"{segs:02d}"
        return f"{mins_s}:{segs_s}"
