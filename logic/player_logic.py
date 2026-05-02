# -*- coding: utf-8 -*-
import os
import random

from alchemy.database import init_db
from alchemy.factory import Factory_songs
from data.db import dataBase
from data.SongsFactory import SongsFactory
from data.RadiosFactory import RadiosFactory
from logic.config import Modes, ManagerModes
from lyrics.engine import LyricsSearcher
from player.vlc_backend import mp3player


class PlayerLogic:

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
        return random.randint(0, 1000000000)

    def random_song(self, current_index, max):
        if max > 1:
            randomSong = random.randint(0, max)
            while randomSong == current_index:
                randomSong = random.randint(0, max)
            return randomSong
        return False

    def check_exists(self, path):
        return os.path.exists(path)

    def change_volume(self, value):
        self.player.change_volume(value)

    def search_lyrics(self, song, artist):
        lyric = LyricsSearcher(song, artist)
        return lyric.get_lyrics()

    def lyrics_searcher(self, song, artist):
        return LyricsSearcher(song, artist)


class PlayerDataLogic:

    db = dataBase()
    factory_songs = SongsFactory()
    factory_radios = RadiosFactory()

    def createTable(self):
        init_db()
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

    def list_files(self, paths):
        return Factory_songs().list_files(paths)

    def delete_song(self, id):
        Factory_songs().delete_by_id(id)

    def bump_play_count(self, song_id):
        try:
            Factory_songs().bump_play_count(int(song_id))
        except Exception:
            pass

    def smart_filter(self, kind, limit=200):
        return Factory_songs().smart_filter(kind, limit)

    def update_song_tags(self, song_id, **fields):
        from alchemy.model import Song
        from alchemy.database import Session
        session = Session()
        obj = session.query(Song).get(song_id)
        if obj is None:
            return
        for k, v in fields.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        session.commit()

    def find_orphans(self):
        from alchemy.model import Song
        from alchemy.database import Session
        session = Session()
        return [s for s in session.query(Song).all()
                if not s.path or not os.path.exists(s.path)]
