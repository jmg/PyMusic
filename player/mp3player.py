# -*- coding: utf-8 -*-
import pygame
import threading
import gtk

pygame.init()
gtk.gdk.threads_init()

class eventListener(threading.Thread):

    def __init__(self, next):
        threading.Thread.__init__(self)
        self.next = next
        self.fin = False

    def run(self):
        while not pygame.event.get():
            gtk.gdk.threads_enter()
            gtk.gdk.threads_leave()
        self.next()

    def __del__(self):
        del(self)

class showPos(threading.Thread):

    def __init__(self, clock, getPosition, entry, song):
        threading.Thread.__init__(self)
        self.clock = clock
        self.getPosition = getPosition
        self.entry = entry
        self.song = song

    def run(self):
        self.segs = 0
        self.spaces = ""
        self.i = 0

        while pygame.mixer.music.get_busy():
            gtk.gdk.threads_enter()

            self.clock.set_text(self.getPosition())
            #self.moveText()

            gtk.gdk.threads_leave()

    def moveText(self):
        #toma los segundos del string de tiempo
        if int(self.getPosition()[3:5]) != self.segs:
            leng = len(self.song)
            title = self.song
            self.spaces = self.spaces.zfill(self.i).replace("0"," ")

            self.entry.set_text(self.spaces + title)

            self.segs = int(self.getPosition()[3:5])
            self.i += 1

    def __del__(self):
        del(self)
        print "Destroy"

class showVideo(threading.Thread):

    def __init__(self, movie):
        threading.Thread.__init__(self)
        self.movie = movie

    def run(self):
        while 1:
            self.movie.play()


class mp3player:

    def getFileName(self):
        return self.fileName

    def __init__(self):
        pygame.mixer.music.set_endevent(pygame.constants.USEREVENT)
        self.playing = False

    def play(self,fileName):
        self.fileName = fileName
        pygame.mixer.init(44100)

        pygame.mixer.music.load(fileName)
        movie = pygame.movie.Movie(fileName)
        if movie.has_video():
            pygame.display.init()
            screen = pygame.display.set_mode(movie.get_size())
            pygame.time.wait(200)
            movie.set_display(screen)
            pygame.mixer.music.play()
            video = showVideo(movie)
            video.start()
        else:
            pygame.mixer.music.load(fileName)
            pygame.mixer.music.play()
        self.playing = True

    def stop(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.playing = False

    def pause(self):
        pygame.mixer.music.pause()
        self.playing = False

    def resume(self):
        pygame.mixer.music.unpause()
        self.playing = True

    def getPosition(self):
        milisegs = pygame.mixer.music.get_pos() % 1000
        time = pygame.mixer.music.get_pos() /1000
        mins = time / 60
        segs = time % 60
        if mins < 10:
            mins = "0"+str(mins)
        else:
            mins = str(mins)
        if segs < 10:
            segs = "0"+str(segs)
        else:
            segs = str(segs)
        if milisegs < 10:
            milisegs = "00"+str(milisegs)
        elif milisegs < 100:
            milisegs = "0"+str(milisegs)
        else:
            milisegs = str(milisegs)

        return mins+":"+segs+"."+milisegs

    def change_volume(self, value):
        pygame.mixer.music.set_volume(value)

    def isPlaying(self):
        if self.playing:
            return True
        return False


