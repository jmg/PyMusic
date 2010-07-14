# -*- coding: utf-8 -*-
import pygtk
import gtk
import gstreamer
import sys
import db
import os
import tags
import random
import console

class Interfaz(object):

    store = gtk.ListStore(str,str,str,str,str,str)
    player = gstreamer.mp3player()
    dba = db.dataBase()
    randomize = False
    MUSIC = 1
    RADIO = 2
    mode = MUSIC

    def __init__(self):

        self.builder = gtk.Builder()
        #/home/jm/Documentos/PyMp3/
        self.builder.add_from_file('interfaces/minimal.xml')
        self.builder.connect_signals({
        'play' : self.play ,
        'stop' : self.stop ,
        'pause' : self.pause ,
        'LoadFIle' : self.loadFile ,
        'selectFile' : self.selectFile ,
        'key' : self.keyPress ,
        'DoubleClick' : self.doubleClick,
        'finderKeyPressed' : self.finder,
        'selectDir' : self.loadDir,
        'volumeChanged' : self.volumeChanged,
        'Resume' : self.resume,
        'Radios': self.radioManager,
        'selectedDir' : self.updateSongs,
        'addRadio': self.addRadio,
        'Musica': self.musicManager,
        'addUri': self.addUri,
        'cancelUri': self.cancelUri,
        'seek' : self.seek,
        'menu_randomizer' : self.randomizer,
        'cancelRandomList' : self.cancelRandomList,
        'aceptRandomList' : self.aceptRandomList,
        'randomList' : self.randomPlay,
        'scoreAccept' : self.scoreAccept,
        'scoreCancel' : self.scoreCancel,
        'RankingShow' : self.rankingShow
        })

        self.window = self.builder.get_object('window1')
        self.entry = self.builder.get_object('entry1')
        self.clock = self.builder.get_object('entry2')
        self.filedl = self.builder.get_object('filechooserdialog1')
        self.list = self.builder.get_object('treeview2')
        self.finderBox = self.builder.get_object('finder')
        self.dirdl = self.builder.get_object('filechooserdialog2')
        self.playButton = self.builder.get_object('Play')
        self.volumeBar = self.builder.get_object('volumen')
        self.pauseButton = self.builder.get_object('Pause')
        self.resumeButton = self.builder.get_object('Resume')
        self.radioButton = self.builder.get_object('Radios')
        self.addRadioButton = self.builder.get_object('AddRadio')
        self.addDirectoryButton = self.builder.get_object('UpdateSongs')
        self.musicButton = self.builder.get_object('Musica')
        self.radioUriWindow = self.builder.get_object('RadioUriWindow')
        self.radioUri = self.builder.get_object('radioUri')
        self.seekBar = self.builder.get_object('seekBar')
        self.randomListWindow = self.builder.get_object('RandomListWindow')
        self.randomListPath = self.builder.get_object('RandomListPath')
        self.randomListSize = self.builder.get_object('RandomListSize')
        self.randomFilter = self.builder.get_object('RandomizeFilter')
        self.scoreWindow = self.builder.get_object('scoreWindow')
        self.scoreCombo = self.builder.get_object('scoreCombo')
        self.scoresViewWindow = self.builder.get_object('scoresViewWindow')
        self.listRanking = self.builder.get_object('RankingGrid')


        self.window.connect("delete_event", gtk.main_quit)
        self.window.connect("destroy", gtk.main_quit)

        #conecta los eventos de cierre de widget con metodos q los ocultan en vez de destruirlos
        self.filedl.connect("delete_event", self.selectFile)
        self.filedl.connect("destroy", self.selectFile)
        self.dirdl.connect("delete_event", self.updateSongs)
        self.dirdl.connect("destroy", self.updateSongs)
        self.radioUriWindow.connect("delete_event", self.cancelUri)
        self.radioUriWindow.connect("destroy", self.cancelUri)
        self.randomListWindow.connect("delete_event", self.cancelRandomList)
        self.randomListWindow.connect("destroy", self.cancelRandomList)
        self.scoreWindow.connect("delete_event", self.scoreCancel)
        self.scoreWindow.connect("destroy", self.scoreCancel)
        self.scoresViewWindow.connect("delete_event", self.hideRanking)
        self.scoresViewWindow.connect("destroy", self.hideRanking)

        self.rank = RankingDataView(self.listRanking)

        self.showPos = None
        self.textMovement = None
        self.moveBar = None

        self.popup = Menu(self.scoreSong, self.copy)

        #establece el modelo y las columnas del GtktreeView
        self.list.set_model(self.store)
        self.col = gtk.TreeViewColumn("Dir", gtk.CellRendererText(), text=0)
        self.col2 = gtk.TreeViewColumn("Tema", gtk.CellRendererText(), text=1)
        self.col3 = gtk.TreeViewColumn("Artísta", gtk.CellRendererText(), text=2)
        self.col4 = gtk.TreeViewColumn("Album", gtk.CellRendererText(), text=3)
        self.col5 = gtk.TreeViewColumn("Año", gtk.CellRendererText(), text=4)
        self.col6 = gtk.TreeViewColumn("id", gtk.CellRendererText(), text=5)
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

        self.initializeSongs()
        self.initializeRadios()
        self.initializePunctuations()
        self.window.show()

    def play(self, sender):

        self.id = self.generateId()

        self.player.stop()

        if not self.randomize or self.mode == self.RADIO:
            self.player.play(self.songToPlay(), self.next, self.id)
        else:
            self.player.play(self.randomSongToPlay(), self.next, self.id)

        self.showPos = gstreamer.showPos(self.clock, self.player, self.entry, self.titleOfSong, self.id)
        self.showPos.start()

        self.moveBar = gstreamer.moveBar(self.seekBar, self.player, self.id)
        self.moveBar.start()

        self.window.set_title(self.titleOfSong)

        self.pauseButton.show()
        self.resumeButton.hide()


    def generateId(self):
        return random.randint(0,1000000000)

    def stop(self, sender):
        if self.player.isPlaying():
            self.player.stop()
            self.pauseButton.show()
            self.resumeButton.hide()

    def resume(self, sender):
        if not self.player.isPlaying():
            self.player.resume()
            self.resumeButton.hide()
            self.pauseButton.show()

    def pause(self, sender):
        if self.player.isPlaying():
            self.player.pause()
            self.pauseButton.hide()
            self.resumeButton.show()

    def seek(self, sender, value, unknow):
        pass

    def next(self):

        self.stop(self.next)

        if not self.randomize and self.iter[0][0] < len(self.store) - 1:
            self.list.set_cursor(self.iter[0][0]+1)
        else:
            self.list.set_cursor(0)

        self.play(self.next)

    def songToPlay(self):
        self.iter = self.list.get_cursor()
        if self.iter != (None, None):
            iter = self.iter[0][0]
        else:
            iter = 0
            self.list.set_cursor(0)
            self.iter = self.list.get_cursor()
        songToPlay = self.store.get_value(self.store.get_iter(iter),0)
        self.titleOfSong = self.store.get_value(self.store.get_iter(iter),1)
        self.entry.set_text(self.titleOfSong)
        while not self.checkExists(songToPlay):
            if self.iter[0][0] < len(self.store) - 1:
                self.list.set_cursor(self.iter[0][0] + 1)
            else:
                self.list.set_cursor(0)
            if self.iter != (None, None):
                iter = self.iter[0][0]
            else:
                iter = 0
                self.list.set_cursor(0)
            songToPlay = self.store.get_value(self.store.get_iter(iter),0)
            self.titleOfSong = self.store.get_value(self.store.get_iter(iter),1)
            self.entry.set_text(self.titleOfSong)
        return songToPlay

    def randomSongToPlay(self):
        randomSongToPlay = self.randomSong()
        songToPlay = self.store.get_value(self.store.get_iter(randomSongToPlay),0)
        self.titleOfSong = self.store.get_value(self.store.get_iter(randomSongToPlay),1)
        self.list.set_cursor(randomSongToPlay)
        self.entry.set_text(self.titleOfSong)
        while not self.checkExists(songToPlay):
            randomSongToPlay = self.randomSong()
            songToPlay = self.store.get_value(self.store.get_iter(randomSongToPlay),0)
            self.titleOfSong = self.store.get_value(self.store.get_iter(randomSongToPlay),1)
            self.list.set_cursor(randomSongToPlay)
            self.entry.set_text(self.titleOfSong)
        return songToPlay

    def checkExists(self, path):
        if not os.path.exists(path) and self.mode == self.MUSIC:
            self.deleteSong()
            return False
        return True

    def randomSong(self):
        max = len(self.store) - 1
        try:
            actual = self.iter[0][0]
        except:
            actual = 0

        if max > 1:
            randomSong = random.randint(0,max)
            while randomSong == actual:
                randomSong = random.randint(0,max)
            return randomSong
        return False

    def loadFile(self, sender):
        self.filedl.set_select_multiple(True)
        self.filedl.show()

    def selectFile(self, sender, destroyer=None):
        self.filedl.hide()
        if self.filedl.get_filename():
            fullPath = str(self.filedl.get_filename())
            dir = fullPath.rpartition("/")
            self.entry.set_text(dir[2])
            self.listLoad(self.filedl.get_filenames())
        return True

    def loadDir(self, sender):
        if sender != self.copy:
            self.dirdl.set_title("Cargar Temas")
            self.dirdl.show()
        else:
            self.dirdl.set_title("Copiar Tema")
            self.dirdl.show()

    def keyPress(self, sender, key):
        if key.keyval == 65535:
            self.deleteSong()
        if key.keyval == 65293 or key.keyval == 65421 or key.keyval == 32:
            self.play(self.keyPress)

    def deleteSong(self):
        self.iter = self.list.get_cursor()
        self.dba.deleteSong(self.store.get_value(self.store.get_iter(self.iter[0][0]),0))
        path = self.store.get_path(self.store.get_iter(self.iter[0][0]))
        treeiter = self.store.get_iter(path)
        self.store.remove(treeiter)

    def doubleClick(self, sender, click):
        if click.button == 3:
            self.popup.makeMenu(click)
        if click.type == gtk.gdk._2BUTTON_PRESS:
            self.play(self.doubleClick)

    def initializeSongs(self):
        self.dba.createTable()
        tagedSongs = self.dba.fetchSongs()
        self.listLoad(tagedSongs)

    #Actualiza los archivos de la base de datos
    def updateSongs(self, sender, destroyer=None):
        self.dirdl.hide()
        if self.dirdl.get_filename():
            if self.dirdl.get_title() == "Cargar Temas":
                dir = self.dirdl.get_filename()
                self.dba.insertSongs(self.dba.listDir(dir))
                songs = []
                tagedSongs = self.dba.fetchSongs()
                self.listLoad(tagedSongs)
            else:
                dir = self.dirdl.get_filename()
                self.copySong(dir)
        return True

    #carga los archivos en el gtktreeview
    def listLoad(self, songs):
        for song in songs:
            dirSong = song[0].rpartition("/")
            self.store.append([dirSong[0]+"/"+dirSong[2],dirSong[2], song[1], song[2], song[3], song[4]])

    def finder(self, sender, key):
        if key.keyval == 65293 or key.keyval == 65421:
            songs = []
            tagedSongs = self.dba.fetchMany(self.finderBox.get_text())
            self.store.clear()
            self.listLoad(tagedSongs)

    def volumeChanged(self, sender, x ,y):
        self.player.changeVolume(self.volumeBar.get_value() /100)

    def radioManager(self, sender):
        self.addRadioButton.show()
        self.musicButton.show()

        #vuelve a cargar las Radios
        self.store.clear()
        self.initializeRadios()
        self.mode = self.RADIO

        self.addDirectoryButton.hide()
        self.radioButton.hide()

    def addRadio(self,sender):
        self.radioUriWindow.show()

    def musicManager(self, sender):
        self.radioButton.show()
        self.addDirectoryButton.show()

        #vuelve a cargar la musica
        self.store.clear()
        self.initializeSongs()
        self.mode = self.MUSIC

        self.addRadioButton.hide()
        self.musicButton.hide()

    def addUri(self, sender):
        self.dba.insertRadio(self.radioUri.get_text())
        self.store.clear()
        self.radioUri.set_text("")
        self.radioUriWindow.hide()
        self.updateRadios()

    def cancelUri(self, sender, destroyer=None):
        self.radioUri.set_text("")
        self.radioUriWindow.hide()
        return True

    def initializeRadios(self):
        self.dba.createTableRadios()
        self.updateRadios()

    def updateRadios(self):
        radios = self.dba.fetchRadios()
        self.listLoad(radios)

    def randomizer(self, sender):
        self.randomListWindow.show()

    def aceptRandomList(self, sender):
        condition = self.randomFilter.get_text()
        songs = self.dba.fetchRandomSongs(condition)
        path = self.randomListPath.get_text()
        size = int(self.randomListSize.get_text())
        generatList = randomList(songs, size, path)
        generatList.start()
        print "generating list..."
        self.randomListWindow.hide()

    def cancelRandomList(self, sender, destroyer=None):
        self.randomListWindow.hide()
        return True

    def randomPlay(self, sender):
        if self.randomize:
            self.randomize = False
        else:
            self.randomize = True

    def initializePunctuations(self):
        self.dba.createTablePunctuation()

    def scoreSong(self, sender):
        self.scoreWindow.show()

    def scoreAccept(self, sender):
        iter = self.list.get_cursor()
        IdsongToScore = self.store.get_value(self.store.get_iter(iter[0][0]),5)
        score = self.scoreCombo.get_text()
        self.dba.scoreSong(IdsongToScore, int(score))
        self.scoreWindow.hide()

    def scoreCancel(self, sender, destroyer = None):
        self.scoreWindow.hide()
        return True

    def rankingShow(self, sender):
        self.rank.fillDataRanking(self.dba.fetchSongsScores())
        self.scoresViewWindow.show()

    def hideRanking(self, sender, destroyer = None):
        self.scoresViewWindow.hide()
        return True

    def copy(self, sender):
        self.loadDir(self.copy)

    def copySong(self, destination):
        iter = self.list.get_cursor()
        dir = self.store.get_value(self.store.get_iter(iter[0][0]),0)
        command = 'cp "'+ dir + '" "' + destination + '"'
        os.system(command)
        print command


class Menu:

    def __init__(self, score, copy):
        self.score = score
        self.copy = copy

    def makeMenu(self, click):

        self.menu = gtk.Menu()
        self.points = gtk.CheckMenuItem("Calificar Canción", False)
        self.separator = gtk.SeparatorMenuItem()
        self.fileCopy = gtk.CheckMenuItem("Copiar Tema", False)

        self.menu.append(self.points)
        self.menu.append(self.separator)
        self.menu.append(self.fileCopy)

        self.points.connect("activate", self.score)
        self.fileCopy.connect("activate", self.copy)

        self.points.show()
        self.separator.show()
        self.fileCopy.show()

        self.menu.popup(None, None, None, click.button, click.time)

        return True

class RankingDataView:

    def __init__(self, listRanking):
        self.listRanking = listRanking
        self.storeRanking = gtk.ListStore(str,str)
        self.listRanking.set_model(self.storeRanking)
        self.col1 = gtk.TreeViewColumn("Tema", gtk.CellRendererText(), text=0)
        self.col2 = gtk.TreeViewColumn("Calificacion", gtk.CellRendererText(), text=1)
        self.listRanking.append_column(self.col1)
        self.listRanking.append_column(self.col2)
        self.col1.set_max_width(300)
        self.col2.set_max_width(100)

    def fillDataRanking(self, songs):
        self.storeRanking.clear()
        for song in songs:
            dirSong = song[0].rpartition("/")
            self.storeRanking.append([dirSong[2], song[1]])


class randomList(gstreamer.threading.Thread):

    def __init__(self, songs, size, path):
        gstreamer.threading.Thread.__init__(self)
        self.size = size
        self.songs = songs
        self.path = path

    def run(self):
        self.size *= 1024 #bytes to kilo
        self.size *= 1024 #kilo to mega
        #self.size *= 1024 #mega to giga
        acum = 0
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        for song in self.songs:
            try:
                filesize = os.path.getsize(song[0])
            except:
                continue
            acum += filesize
            if self.size <= acum:
                break
            command = 'cp "'+ song[0] + '" "' + self.path + '"'
            print command
            try:
                os.system(command)
            except:
                acum -= filesize
                continue


if __name__ == '__main__':

    if len(sys.argv) > 1:
        console.ConsoleProxy(sys.argv[1:])
    else:
        gtkmp3 = Interfaz()
        gtkmp3.window.show()
        gtk.main()


