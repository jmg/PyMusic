# -*- coding: utf-8 -*-
import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from interfaces.guiThreads import ShowPosThread, MoveBarThread, RandomListThread
from interfaces.configuration import binding_dict
from logic.player_logic import PlayerLogic, PlayerDataLogic
from data.db import dataBase


class MainWindow:

    store = Gtk.ListStore(str, str, str, str, str, str)
    dba = dataBase()
    logic = PlayerLogic()
    data_logic = PlayerDataLogic()

    def __init__(self):
        """Initialise the GTK interface."""
        self.builder = Gtk.Builder()
        self.builder.add_from_file('interfaces/glade/minimal.xml')

        self.builder.connect_signals(
            {k: getattr(self, v) for k, v in binding_dict.items()}
        )

        self.window = self.builder.get_object('window1')
        self.entry = self.builder.get_object('entry1')
        self.clock = self.builder.get_object('entry2')
        self.file_dl = self.builder.get_object('filechooserdialog1')
        self.list = self.builder.get_object('treeview2')
        self.finder_box = self.builder.get_object('finder')
        self.dir_dl = self.builder.get_object('filechooserdialog2')
        self.play_nutton = self.builder.get_object('Play')
        self.volume_bar = self.builder.get_object('volumen')
        self.pause_button = self.builder.get_object('Pause')
        self.resume_button = self.builder.get_object('Resume')
        self.radio_button = self.builder.get_object('Radios')
        self.add_radio_button = self.builder.get_object('AddRadio')
        self.add_directory_button = self.builder.get_object('UpdateSongs')
        self.music_button = self.builder.get_object('Musica')
        self.radio_uri_window = self.builder.get_object('RadioUriWindow')
        self.radio_uri = self.builder.get_object('radioUri')
        self.seek_bar = self.builder.get_object('seekBar')
        self.random_list_window = self.builder.get_object('RandomListWindow')
        self.random_list_path = self.builder.get_object('random_list_path')
        self.random_list_size = self.builder.get_object('random_list_size')
        self.random_filter = self.builder.get_object('RandomizeFilter')
        self.score_window = self.builder.get_object('score_window')
        self.score_combo = self.builder.get_object('score_combo')
        self.scores_view_window = self.builder.get_object('scores_view_window')
        self.list_ranking = self.builder.get_object('RankingGrid')
        self.title_of_song = self.builder.get_object('titleOfSong')

        # extra binding signals
        self.window.connect("delete_event", Gtk.main_quit)
        self.window.connect("destroy", Gtk.main_quit)

        self.rank = RankingDataView(self.list_ranking)

        self.showPos = None
        self.textMovement = None
        self.moveBar = None

        self.popup = Menu(self.score_song, self.copy)

        # GtkTreeView model + columns
        self.list.set_model(self.store)
        self.col = Gtk.TreeViewColumn("Dir", Gtk.CellRendererText(), text=0)
        self.col2 = Gtk.TreeViewColumn("Tema", Gtk.CellRendererText(), text=1)
        self.col3 = Gtk.TreeViewColumn("Artísta", Gtk.CellRendererText(), text=2)
        self.col4 = Gtk.TreeViewColumn("Album", Gtk.CellRendererText(), text=3)
        self.col5 = Gtk.TreeViewColumn("Año", Gtk.CellRendererText(), text=4)
        self.col6 = Gtk.TreeViewColumn("id", Gtk.CellRendererText(), text=5)
        self.list.append_column(self.col)
        self.col.set_visible(False)
        self.list.append_column(self.col2)
        self.list.append_column(self.col3)
        self.list.append_column(self.col4)
        self.list.append_column(self.col5)
        self.list.append_column(self.col6)
        self.col6.set_visible(False)
        self.col2.set_max_width(500)
        self.col3.set_max_width(200)
        self.col4.set_max_width(200)
        self.col5.set_max_width(100)

        self.initialize_songs()
        self.initialize_radios()
        self.initialize_punctuations()
        self.window.show()

    def play(self, sender):
        if self.logic.mode == self.logic.modes.NORMAL_PLAY:
            song = self.song_to_play()
        elif self.logic.mode == self.logic.modes.RANDOM_PLAY:
            song = self.random_song_to_play()
        else:
            return

        self.id = self.logic.play(song, self.next)

        self.showPosThread = ShowPosThread(
            self.clock, self.entry, self.title_of_song, self.logic.player, self.id)
        self.showPosThread.start()

        self.moveBarThread = MoveBarThread(self.seek_bar, self.logic.player, self.id)
        self.moveBarThread.start()

        self.window.set_title(self.title_of_song)

        self.pause_button.show()
        self.resume_button.hide()

    def stop(self, sender):
        self.logic.stop()
        self.pause_button.show()
        self.resume_button.hide()

    def resume(self, sender):
        self.logic.resume()
        self.resume_button.hide()
        self.pause_button.show()

    def pause(self, sender):
        self.logic.pause()
        self.pause_button.hide()
        self.resume_button.show()

    def is_playing(self):
        return self.logic.is_playing()

    def seek(self, sender, value, unknow):
        pass

    def next(self):
        self.stop(self.next)
        self.set_next_index()
        self.play(self.next)

    def get_current_index(self):
        return self.list.get_cursor()

    def get_list_len(self):
        return len(self.store)

    def set_next_index(self):
        index = self.get_current_index()[0][0]
        if index < self.get_list_len() - 1:
            self.list.set_cursor(index + 1)
        else:
            self.list.set_cursor(0)

    def song_to_play(self):
        self.iter = self.list.get_cursor()
        if self.iter != (None, None):
            iter_idx = self.iter[0][0]
        else:
            iter_idx = 0
            self.list.set_cursor(0)
            self.iter = self.list.get_cursor()
        song_to_play = self.store.get_value(self.store.get_iter(iter_idx), 0)
        self.title_of_song = self.store.get_value(self.store.get_iter(iter_idx), 1)
        self.entry.set_text(self.title_of_song)

        while not self.check_exists(song_to_play):
            if self.iter[0][0] < len(self.store) - 1:
                self.list.set_cursor(self.iter[0][0] + 1)
            else:
                self.list.set_cursor(0)
            if self.iter != (None, None):
                iter_idx = self.iter[0][0]
            else:
                iter_idx = 0
                self.list.set_cursor(0)
            song_to_play = self.store.get_value(self.store.get_iter(iter_idx), 0)
            self.title_of_song = self.store.get_value(self.store.get_iter(iter_idx), 1)
            self.entry.set_text(self.title_of_song)
        return song_to_play

    def random_song_to_play(self):
        try:
            current_index = self.iter[0][0]
        except Exception:
            current_index = 0

        randomSongToPlay = self.logic.random_song(current_index, len(self.store) - 1)

        songToPlay = self.store.get_value(self.store.get_iter(randomSongToPlay), 0)
        self.title_of_song = self.store.get_value(self.store.get_iter(randomSongToPlay), 1)
        self.list.set_cursor(randomSongToPlay)
        self.entry.set_text(self.title_of_song)
        while not self.check_exists(songToPlay):
            randomSongToPlay = self.logic.random_song(current_index, len(self.store) - 1)
            songToPlay = self.store.get_value(self.store.get_iter(randomSongToPlay), 0)
            self.title_of_song = self.store.get_value(self.store.get_iter(randomSongToPlay), 1)
            self.list.set_cursor(randomSongToPlay)
            self.entry.set_text(self.title_of_song)
        return songToPlay

    def check_exists(self, path):
        return self.logic.check_exists(path)

    def load_file(self, sender):
        self.file_dl.set_select_multiple(True)
        self.file_dl.show()

    def select_file(self, sender, destroyer=None):
        self.file_dl.hide()
        if self.file_dl.get_filename():
            fullPath = str(self.file_dl.get_filename())
            dir_part = fullPath.rpartition("/")
            self.entry.set_text(dir_part[2])
            self.list_load(self.file_dl.get_filenames())
        return True

    def load_dir(self, sender):
        if sender != self.copy:
            self.dir_dl.set_title("Cargar Temas")
        else:
            self.dir_dl.set_title("Copiar Tema")
        self.dir_dl.show()

    def key_press(self, sender, key):
        if key.keyval == 65535:
            self.delete_song()
        if key.keyval in (65293, 65421, 32):
            self.play(self.key_press)

    def delete_song(self):
        self.iter = self.list.get_cursor()
        song = self.store.get_value(self.store.get_iter(self.iter[0][0]), 0)
        self.logic.delete_song(song)
        path = self.store.get_path(self.store.get_iter(self.iter[0][0]))
        treeiter = self.store.get_iter(path)
        self.store.remove(treeiter)

    def double_click(self, sender, click):
        if click.button == 3:
            self.popup.makeMenu(click)
        if click.type == Gdk.EventType._2BUTTON_PRESS:
            self.play(self.double_click)

    def initialize_songs(self):
        self.data_logic.createTable()
        taged_songs = self.data_logic.fetch_all_songs()
        self.list_load(taged_songs)

    # Actualiza los archivos de la base de datos
    def add_songs(self, sender, destroyer=None):
        self.dir_dl.hide()
        if self.dir_dl.get_filename():
            if self.dir_dl.get_title() == "Cargar Temas":
                dir_path = self.dir_dl.get_filename()
                self.data_logic.add_songs(self.data_logic.list_dir(dir_path))
                tagedSongs = self.data_logic.fetch_all_songs()
                self.list_load(tagedSongs)
            else:
                self.copy_song(self.dir_dl.get_filename())
        return True

    def list_load(self, songs):
        for song in songs:
            complete_name = song.path.rpartition("/")
            name = complete_name[2]
            self.store.append([song.path, name, song.artist, song.album, str(song.year), str(song.id)])

    def finder(self, sender, key):
        if key.keyval in (65293, 65421):
            taged_songs = self.data_logic.find(self.finder_box.get_text())
            self.store.clear()
            self.list_load(taged_songs)

    def volume_changed(self, sender, x, y):
        self.logic.change_volume(self.volume_bar.get_value() / 100)

    def btRadioMusic_click(self, sender):
        if self.logic.get_man_mode() == self.logic.man_modes.NORMAL:
            self.radio_manager(sender)
            self.logic.set_man_mode(self.logic.man_modes.RADIO)
        elif self.logic.get_man_mode() == self.logic.man_modes.RADIO:
            self.music_manager(sender)
            self.logic.set_man_mode(self.logic.man_modes.NORMAL)

    def radio_manager(self, sender):
        self.add_radio_button.show()
        self.music_button.show()
        self.store.clear()
        self.initialize_radios()
        self.add_directory_button.hide()
        self.radio_button.hide()

    def add_radio(self, sender):
        self.radio_uri_window.show()

    def music_manager(self, sender):
        self.radio_button.show()
        self.add_directory_button.show()
        self.store.clear()
        self.initialize_songs()
        self.add_radio_button.hide()
        self.music_button.hide()

    def add_uri(self, sender):
        self.data_logic.add_radio(self.radio_uri.get_text())
        self.store.clear()
        self.radio_uri.set_text("")
        self.radio_uri_window.hide()
        self.update_radios()

    def cancel_uri(self, sender, destroyer=None):
        self.radio_uri.set_text("")
        self.radio_uri_window.hide()
        return True

    def initialize_radios(self):
        self.data_logic.create_table_radios()
        self.update_radios()

    def update_radios(self):
        radios = self.data_logic.fetch_radios()
        self.list_load(radios)

    def randomizer(self, sender):
        self.random_list_window.show()

    def accept_random_list(self, sender):
        condition = self.random_filter.get_text()
        songs = self.dba.fetchRandomSongs(condition)
        path = self.random_list_path.get_text()
        size = int(self.random_list_size.get_text())
        generatList = RandomListThread(songs, size, path)
        generatList.start()
        print("generating list...")
        self.random_list_window.hide()

    def cancel_random_list(self, sender, destroyer=None):
        self.random_list_window.hide()
        return True

    def random_play(self, sender):
        if self.logic.get_mode() == self.logic.modes.RANDOM_PLAY:
            self.logic.set_mode(self.logic.modes.NORMAL_PLAY)
        else:
            self.logic.set_mode(self.logic.modes.RANDOM_PLAY)

    def initialize_punctuations(self):
        self.dba.createTablePunctuation()

    def score_song(self, sender):
        self.score_window.show()

    def score_accept(self, sender):
        iter_pos = self.list.get_cursor()
        IdsongToScore = self.store.get_value(self.store.get_iter(iter_pos[0][0]), 5)
        score = self.score_combo.get_text()
        self.dba.scoreSong(IdsongToScore, int(score))
        self.score_window.hide()

    def score_cancel(self, sender, destroyer=None):
        self.score_window.hide()
        return True

    def ranking_show(self, sender):
        self.rank.fillDataRanking(self.data_logic.fetch_songs_scores())
        self.scores_view_window.show()

    def hide_ranking(self, sender, destroyer=None):
        self.scores_view_window.hide()
        return True

    def copy(self, sender):
        self.load_dir(self.copy)

    def copy_song(self, destination):
        iter_pos = self.list.get_cursor()
        dir_path = self.store.get_value(self.store.get_iter(iter_pos[0][0]), 0)
        command = f'cp "{dir_path}" "{destination}"'
        os.system(command)
        print(command)


class Menu:

    def __init__(self, score, copy):
        self.score = score
        self.copy = copy

    def makeMenu(self, click):
        self.menu = Gtk.Menu()
        self.points = Gtk.CheckMenuItem.new_with_label("Calificar Canción")
        self.separator = Gtk.SeparatorMenuItem()
        self.fileCopy = Gtk.CheckMenuItem.new_with_label("Copiar Tema")

        self.menu.append(self.points)
        self.menu.append(self.separator)
        self.menu.append(self.fileCopy)

        self.points.connect("activate", self.score)
        self.fileCopy.connect("activate", self.copy)

        self.points.show()
        self.separator.show()
        self.fileCopy.show()

        self.menu.popup(None, None, None, None, click.button, click.time)

        return True


class RankingDataView:

    def __init__(self, list_ranking):
        self.list_ranking = list_ranking
        self.storeRanking = Gtk.ListStore(str, str)
        self.list_ranking.set_model(self.storeRanking)
        self.col1 = Gtk.TreeViewColumn("Tema", Gtk.CellRendererText(), text=0)
        self.col2 = Gtk.TreeViewColumn("Calificacion", Gtk.CellRendererText(), text=1)
        self.list_ranking.append_column(self.col1)
        self.list_ranking.append_column(self.col2)
        self.col1.set_max_width(300)
        self.col2.set_max_width(100)

    def fillDataRanking(self, songs):
        self.storeRanking.clear()
        for song in songs:
            dirSong = song.path.rpartition("/")
            self.storeRanking.append([dirSong[2], song.path])
