# -*- coding: utf-8 -*-
import random
import os
from player.gstreamer import mp3player
import db

class Player_Logic(object):

    player = mp3player()
    MUSIC = 2
    mode = MUSIC
    db = db.dataBase()

    def play(self, song):

        self.id = self._generate_id()
        self.player.stop()

        self.next = None
        #if not self.randomize or self.mode == self.RADIO:
        self.player.play(song)
        #else:
        #    self.player.play(self.randomSongToPlay(), self.next, self.id)

        #self.showPos = gstreamer.showPos(self.clock, self.player, self.entry, self.titleOfSong, self.id)
        #self.showPos.start()

        #self.moveBar = gstreamer.moveBar(self.seekBar, self.player, self.id)
        #self.moveBar.start()

        #self.window.set_title(self.titleOfSong)

    def stop(self):

        if self.player.isPlaying():
            self.player.stop()

    def resume(self):

        if not self.player.isPlaying():
            self.player.resume()

    def pause(self):

        if self.player.isPlaying():
            self.player.pause()

    def _generate_id(self):
        return random.randint(0,1000000000)

    def random_song(self, current_index, max):
        if max > 1:
            randomSong = random.randint(0,max)
            while randomSong == current_index:
                randomSong = random.randint(0,max)
            return randomSong
        return False

    def check_exists(self, path):
        if not os.path.exists(path) and self.mode == self.MUSIC:
            self.deleteSong()
            return False
        return True

    def change_volume(self, value):
        self.player.change_volume(value)

    def find(self, filter):
        return self.db.fetchMany(filter)

    def fetch_all_songs(self):
        return self.db.fetchSongs()

    def add_songs(self, songs):
        self.ds.insert_songs(songs)
