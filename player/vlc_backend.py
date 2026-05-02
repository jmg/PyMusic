# -*- coding: utf-8 -*-
"""python-vlc backed mp3 player.

Provides the same interface as :mod:`player.gstreamer` so it can be used
as a drop-in replacement.
"""

import time

try:
    import vlc
    _VLC_AVAILABLE = True
except (ImportError, OSError):
    vlc = None
    _VLC_AVAILABLE = False


class mp3player:

    def __init__(self):
        if _VLC_AVAILABLE:
            self._instance = vlc.Instance("--quiet")
            self.player = self._instance.media_player_new()
            self._event_manager = self.player.event_manager()
            self._event_manager.event_attach(
                vlc.EventType.MediaPlayerEndReached, self._on_end_reached
            )
        else:
            self._instance = None
            self.player = None
            self._event_manager = None
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

        media = self._instance.media_new(self.getUri(path))
        self.player.set_media(media)
        self.player.play()

    def playList(self, listSongs):
        for song in listSongs:
            self.play(song, None, None)

    def getUri(self, path):
        if path.startswith("http://") or path.startswith("https://") or path.startswith("file://"):
            return path
        return "file://" + path

    def stop(self):
        if self.player:
            self.player.stop()

    def resume(self):
        if self.player and not self.isPlaying():
            self.player.play()

    def pause(self):
        if self.player and self.isPlaying():
            self.player.pause()

    def change_volume(self, volume):
        if self.player:
            self.player.audio_set_volume(int(volume * 100))

    # ------------------------------------------------------------------
    # Position queries
    # ------------------------------------------------------------------
    def getPosition(self):
        if not self.player:
            return None
        ms = self.player.get_time()
        if ms < 0:
            return None
        return self.convertTime(ms * 1_000_000)

    def getSeekedPosition(self):
        if not self.player:
            return None
        ms = self.player.get_time()
        if ms < 0:
            return None
        return ms * 1_000_000

    def getSeekableDuration(self):
        if not self.player:
            return -1
        ms = self.player.get_length()
        if ms <= 0:
            return 0
        return ms * 1_000_000

    def seek(self, position):
        if not self.player:
            return
        ms = position // 1_000_000
        self.player.set_time(int(ms))

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------
    def isPlaying(self):
        if not self.player:
            return False
        return bool(self.player.is_playing())

    def isPaused(self):
        if not self.player:
            return False
        return self.player.get_state() == vlc.State.Paused

    # ------------------------------------------------------------------
    # End-of-stream callback
    # ------------------------------------------------------------------
    def _on_end_reached(self, event):
        if self.next:
            self.next()

    def songFinished(self):
        pos = self.getPosition()
        time.sleep(2)
        newPos = self.getPosition()
        return pos == newPos

    def convertTime(self, ns_time):
        time_int = ns_time // 1_000_000_000
        mins = time_int // 60
        segs = time_int % 60
        return f"{mins:02d}:{segs:02d}"
