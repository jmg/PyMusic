# -*- coding: utf-8 -*-
"""Legacy pygame-based mp3 player.

The current default backend is :mod:`player.gstreamer`; this module is kept
around as an alternative backend and has been ported to Python 3.
"""

import threading

try:
    import pygame
    pygame.init()
    _PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    _PYGAME_AVAILABLE = False


class eventListener(threading.Thread):

    def __init__(self, next):
        threading.Thread.__init__(self)
        self.next = next
        self.fin = False

    def run(self):
        if not _PYGAME_AVAILABLE:
            return
        while not pygame.event.get():
            pass
        self.next()


class showPos(threading.Thread):

    def __init__(self, clock, getPosition, entry, song):
        threading.Thread.__init__(self)
        self.clock = clock
        self.getPosition = getPosition
        self.entry = entry
        self.song = song

    def run(self):
        if not _PYGAME_AVAILABLE:
            return
        self.segs = 0
        self.spaces = ""
        self.i = 0

        while pygame.mixer.music.get_busy():
            self.clock.set_text(self.getPosition())

    def moveText(self):
        if int(self.getPosition()[3:5]) != self.segs:
            title = self.song
            self.spaces = self.spaces.zfill(self.i).replace("0", " ")
            self.entry.set_text(self.spaces + title)
            self.segs = int(self.getPosition()[3:5])
            self.i += 1


class showVideo(threading.Thread):

    def __init__(self, movie):
        threading.Thread.__init__(self)
        self.movie = movie

    def run(self):
        while True:
            self.movie.play()


class mp3player:

    def getFileName(self):
        return self.fileName

    def __init__(self):
        if _PYGAME_AVAILABLE:
            pygame.mixer.music.set_endevent(pygame.constants.USEREVENT)
        self.playing = False
        self.fileName = None

    def play(self, fileName):
        self.fileName = fileName
        if not _PYGAME_AVAILABLE:
            return
        pygame.mixer.init(44100)
        pygame.mixer.music.load(fileName)

        movie = getattr(pygame, 'movie', None)
        if movie is not None:
            try:
                m = movie.Movie(fileName)
                if m.has_video():
                    pygame.display.init()
                    screen = pygame.display.set_mode(m.get_size())
                    pygame.time.wait(200)
                    m.set_display(screen)
                    pygame.mixer.music.play()
                    showVideo(m).start()
                    self.playing = True
                    return
            except Exception:
                pass

        pygame.mixer.music.load(fileName)
        pygame.mixer.music.play()
        self.playing = True

    def stop(self):
        if _PYGAME_AVAILABLE and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.playing = False

    def pause(self):
        if _PYGAME_AVAILABLE:
            pygame.mixer.music.pause()
        self.playing = False

    def resume(self):
        if _PYGAME_AVAILABLE:
            pygame.mixer.music.unpause()
        self.playing = True

    def getPosition(self):
        if not _PYGAME_AVAILABLE:
            return "00:00.000"
        ms = pygame.mixer.music.get_pos()
        milisegs = ms % 1000
        time = ms // 1000
        mins = time // 60
        segs = time % 60
        return f"{mins:02d}:{segs:02d}.{milisegs:03d}"

    def changeVolume(self, newValue):
        if _PYGAME_AVAILABLE:
            pygame.mixer.music.set_volume(newValue)

    def isPlaying(self):
        return bool(self.playing)
