import wxversion
wxversion.select("2.8")

import wx
import os
from interfaces.wxWidgets.gui import wxGui
from interfaces.wxFrmAddRadio import wxFrmAddRadio

from logic.player_logic import PlayerLogic, PlayerDataLogic


class MainWindow(wxGui):

    logic = PlayerLogic()
    data_logic = PlayerDataLogic()

    def __init__(self, parent):

        wxGui.__init__(self, parent)

        self.dir_dialog = wx.DirDialog(None, "Choose a Music Folder", style=1 ,defaultPath= ".")

        self.lbSongs.InsertColumn(0,"Path")
        self.lbSongs.SetColumnWidth(0, 0)
        self.lbSongs.InsertColumn(1,"Song")
        self.lbSongs.SetColumnWidth(1, 200)
        self.lbSongs.InsertColumn(2,"Artist")
        self.lbSongs.SetColumnWidth(2, 100)
        self.lbSongs.InsertColumn(3,"Album")
        self.lbSongs.SetColumnWidth(3, 100)
        self.lbSongs.InsertColumn(4,"Year")

        self.lbSongs.InsertColumn(5,"Id")
        self.lbSongs.SetColumnWidth(5, 0)

        self.lbRadios.InsertColumn(0,"Uri")
        self.lbRadios.InsertColumn(1,"Id")
        self.lbRadios.SetColumnWidth(1, 0)

        self.initialize_songs()
        self.initialize_radios()

        #autosize after the list is loaded
        self.lbSongs.SetColumnWidth(4, wx.LIST_AUTOSIZE)
        self.lbRadios.SetColumnWidth(0, wx.LIST_AUTOSIZE)

    def btPlay_click( self, event ):
        self.play(event)

    def lbSongs_dbClick( self, event ):
        self.play(event)

    def lbRadios_dbClick( self, event ):
        self.play_radio(event)

    def btStop_click( self, event ):
        self.stop(event)

    def btPause_click( self, event ):
        self.set_next_index()

    def tgRandom_click( self, event ):
        self.random_play(event)

    def tbFinder_click( self, event):
        self.finder(event)

    def itAddList_click( self, event ):
        self.add_list(event)

    def itAddRadio_click( self, event ):
        self.add_radio(event)

    def lbRadios_keyDown( self, event ):
        self.delete_radio(event)

    def initialize_songs(self):
        self.data_logic.createTable()
        songs = self.data_logic.fetch_all_songs()
        self.list_load(songs)

    def initialize_radios(self):
        self.data_logic.create_table_radios()
        radios = self.data_logic.fetch_radios()
        self.listRadios_load(radios)

    def list_load(self, songs):
        """
            Load the list_ctrl with a list of songs
        """
        self.lbSongs.DeleteAllItems()

        for i, song in enumerate(songs):
            complete_name = song.path.rpartition("/")
            name = complete_name[2]
            dir = complete_name[0]

            index = self.lbSongs.InsertStringItem(100, song.path)
            self.lbSongs.SetStringItem(index, 1, name)
            self.lbSongs.SetStringItem(index, 2, song.artist)
            self.lbSongs.SetStringItem(index, 3, song.album)
            self.lbSongs.SetStringItem(index, 4, song.year)
            self.lbSongs.SetStringItem(index, 5, str(song.id))

    def listRadios_load(self, radios):
        """
            Load the list_ctrl with a list of radios
        """
        self.lbRadios.DeleteAllItems()

        for i, radio in enumerate(radios):
            index = self.lbRadios.InsertStringItem(100, radio.path)
            self.lbRadios.SetStringItem(index, 0, radio.path)
            self.lbRadios.SetStringItem(index, 1, str(radio.id))

    def play(self, event):

        if self.logic.mode == self.logic.modes.NORMAL_PLAY:
            index, path = self.song_to_play()
        elif self.logic.mode == self.logic.modes.RANDOM_PLAY:
            index, path = self.random_song_to_play()

        song = self.lbSongs.GetItem(index, 1).GetText()
        artist = self.lbSongs.GetItem(index, 2).GetText()

        lyrics = self.logic.search_lyrics(song, artist)
        self.tbLyrics.SetValue(lyrics)

        self.id = self.logic.play(path, self.next)

    def play_radio(self, event):

        index, radio_to_play = self.radio_to_play()

        self.id = self.logic.play(radio_to_play, self.next)

    def stop(self, event):
        self.logic.stop()

    def next(self):
        """
            Play the next Song
        """

        self.stop(self.next)
        self.set_next_index()
        self.play(self.next)

    def get_list_len(self):
        return self.lbSongs.GetItemCount()

    def set_next_index(self):
        SEL_FOC = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
        index = self.lbSongs.GetFirstSelected()
        #unselect the current index
        self.lbSongs.SetItemState(index, 0, wx.LIST_STATE_SELECTED)

        if index < self.get_list_len() - 1:
            self.lbSongs.SetItemState(index + 1, SEL_FOC, SEL_FOC)
        else:
            self.lbSongs.SetItemState(0, SEL_FOC, SEL_FOC)

    def set_song(self, index):
        """
            set a song in the textbox and return the name
        """
        SEL_FOC = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
        current_index = self.lbSongs.GetFirstSelected()
        #unselect the current index
        self.lbSongs.SetItemState(current_index, 0, wx.LIST_STATE_SELECTED)

        if index < self.get_list_len() - 1:
            self.lbSongs.SetItemState(index, SEL_FOC, SEL_FOC)
        else:
            self.lbSongs.SetItemState(0, SEL_FOC, SEL_FOC)

        song_to_play = self.lbSongs.GetItem(index, 0).GetText()
        title_of_song = self.lbSongs.GetItem(index, 1).GetText()
        self.tbSong.SetValue(title_of_song)
        return song_to_play

    def set_radio(self, index):
        """
            set a radio in the textbox and return the name
        """
        SEL_FOC = wx.LIST_STATE_SELECTED | wx.LIST_STATE_FOCUSED
        current_index = self.lbRadios.GetFirstSelected()
        #unselect the current index
        self.lbRadios.SetItemState(current_index, 0, wx.LIST_STATE_SELECTED)

        if index < self.get_list_len() - 1:
            self.lbRadios.SetItemState(index, SEL_FOC, SEL_FOC)
        else:
            self.lbRadios.SetItemState(0, SEL_FOC, SEL_FOC)

        radio_to_play = self.lbRadios.GetItem(index, 0).GetText()
        self.tbSong.SetValue(radio_to_play)
        return radio_to_play

    def song_to_play(self):
        """
            Select the current song to play
        """
        index = self.lbSongs.GetFirstSelected()
        song_to_play = self.set_song(index)

        while not self.check_exists(song_to_play):

            index += 1
            song_to_play = self.set_song(index)

        return index, song_to_play

    def random_song_to_play(self):
        """
            Select a random song to play
        """
        random_index = self.logic.random_song(0, self.get_list_len() - 1)
        song_to_play = self.set_song(random_index)

        while not self.check_exists(song_to_play):

            random_index = self.logic.random_song(0, self.get_list_len() - 1)
            song_to_play = self.set_song(random_index)

        return random_index, song_to_play

    def radio_to_play(self):
        """
            Select the current radio to play
        """
        index = self.lbRadios.GetFirstSelected()
        radio_to_play = self.set_radio(index)

        return index, radio_to_play

    def check_exists(self, path):
        """
            Check if exists a path in the file system
        """
        return self.logic.check_exists(path)

    def random_play(self, event):
        """
            set the player mode
            [NORMAL / RANDOM]
        """
        if self.logic.get_mode() == self.logic.modes.RANDOM_PLAY:
            self.logic.set_mode(self.logic.modes.NORMAL_PLAY)
        else:
            self.logic.set_mode(self.logic.modes.RANDOM_PLAY)

    def finder(self, event):
        """
            Find a list of songs by a condition
        """
        #Enter key
        if event.GetKeyCode() == 13:
            songs = self.data_logic.find(self.tbFinder.GetValue())
            self.lbSongs.DeleteAllItems()
            self.list_load(songs)
        else:
            event.Skip()

    def add_list(self, event):
        if self.dir_dialog.ShowModal() == wx.ID_OK:
            dir = self.dir_dialog.GetPath()
            list_dir = self.data_logic.list_dir(dir)
            self.data_logic.add_songs(list_dir)
            songs = self.data_logic.fetch_all_songs()
            self.list_load(songs)

    def add_radio(self, event):
        frmAddRadio = wxFrmAddRadio(self)
        frmAddRadio.ShowModal()
        if frmAddRadio.State == frmAddRadio.OK:
            self.initialize_radios()

    def delete_radio(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE:
            current_index = self.lbRadios.GetFirstSelected()
            id = self.lbRadios.GetItem(current_index, 1).GetText()
            self.data_logic.delete_radio(id)
            self.initialize_radios()


