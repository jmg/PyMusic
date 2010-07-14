# -*- coding: utf-8 -*-
import gst
import os

gtk.gdk.threads_init()

class mp3player:
    
    def __init__(self):
        pass
    
    def play(self, path):
        self.player = gst.element_factory_make("playbin", "player")
        
        uri = self.getUri(path)
        
        print uri
        self.player.set_property('uri', uri)
        self.player.set_state(gst.STATE_PLAYING)
    
    def getUri(self, path):
        if path.find("http://") or path.find("file://"):
            return path
        return "file://" + path

    def stop(self):
        self.player.set_state(gst.STATE_NULL)
        
    def pause(self):
        self.player.set_state(gst.STATE_PAUSED)
        
    def getPosition(self):
        self.player.set_state(gst.STATE_PLAYING)
        
    def getPosition(self):
        return "00:00:00"
        
    def changeVolume(self):
        pass
    
    def is_playing(self):
        return False


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
