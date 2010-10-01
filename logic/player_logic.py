# -*- coding: utf-8 -*-
import random
import os
from player.gstreamer import mp3player
from data.db import dataBase
from data.SongsFactory import SongsFactory
from config import Modes

class PlayerLogic(object):

    player = mp3player()
    modes = Modes()
    mode = Modes.NORMAL_PLAY

    def get_mode(self):
        return self.mode

    def set_mode(self, mode):
        self.mode = mode

    def play(self, song, next=None):

        self.id = self._generate_id()
        self.player.stop()

        self.player.play(song, next, self.id)
        return self.id

    def stop(self):

        if self.player.isPlaying():
            self.player.stop()

    def resume(self):

        if not self.player.isPlaying():
            self.player.resume()

    def pause(self):

        if self.player.isPlaying():
            self.player.pause()

    def is_playing(self):
        return self.player.isPlaying()

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
        if not os.path.exists(path):
            return False
        return True

    def change_volume(self, value):
        self.player.change_volume(value)



class PlayerDataLogic(object):

    db = dataBase()
    factory_songs = SongsFactory()

    def createTable(self):
        self.db.createTable()

    def find(self, filter):
        return self.factory_songs.fetchMany(filter)

    def fetch_all_songs(self):
        return self.factory_songs.fetchSongs()

    def add_songs(self, songs):
        self.factory_songs.insert_songs(songs)

    def fetchRadios(self):
        return []

    def list_dir(self, dir):
        return self.factory_songs.list_dir(dir)




