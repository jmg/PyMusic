# -*- coding: utf-8 -*-
import random
import os

from player.gstreamer import mp3player
from data.db import dataBase
from data.SongsFactory import SongsFactory
from data.RadiosFactory import RadiosFactory
import data.utils
from config import Modes, ManagerModes
from lyrics.engine import LyricsSearcher

from alchemy.factory import *
from alchemy.model import *

class PlayerLogic(object):

    player = mp3player()
    modes = Modes()
    mode = Modes.NORMAL_PLAY
    man_modes = ManagerModes()
    man_mode = ManagerModes.NORMAL

    def get_mode(self):
        return self.mode

    def set_mode(self, mode):
        self.mode = mode

    def get_man_mode(self):
        return self.man_mode

    def set_man_mode(self, man_mode):
        self.man_mode = man_mode

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

    def search_lyrics(self, song, artist):
        lyric = LyricsSearcher(song, artist)
        return lyric.get_lyrics()


class PlayerDataLogic(object):

    db = dataBase()
    factory_songs = SongsFactory()
    factory_radios = RadiosFactory()

    def createTable(self):
        self.factory_songs.createTable()

    def find(self, filter):
        return Factory_songs().fetch_many(filter)

    def fetch_all_songs(self):
        return Factory_songs().fetch_all()

    def add_songs(self, songs):
        factory = Factory_songs()
        for song in songs:
            factory.insert(song)
        factory.commit()

    def fetch_songs_scores(self):
        return self.factory_songs.fetch_all_scores()

    def create_table_radios(self):
        self.factory_radios.create_table()

    def fetch_radios(self):
        return self.factory_radios.fetch_all()

    def add_radio(self, radio):
        self.factory_radios.insert(radio)

    def delete_radio(self, id):
        self.factory_radios.delete(id)

    def list_dir(self, dir):
        return Factory_songs().list_dir(dir)

