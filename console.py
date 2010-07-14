import gstreamer
import sys
import db

class ConsolePlayer:

    Player = gstreamer.mp3player()
    dba = db.dataBase()

    def __init__(self):
        self.dba.createIndexTable()

    def search(self, condition=""):

        songs = self.dba.fetchManyWithId(condition)
        for i,song in enumerate(songs):
            print str(i) + ".-" + song[1]
            self.dba.UpdateIndex(song[0], i)
        self.dba.ResetList();
        self.dba.UpdateList(len(songs) - 1)

    def play(self, song):

        print "Currently Playing => %s" % song
        self.Player.play(song)
        try:
            while not self.Player.songFinished():
                pass
        except KeyboardInterrupt:
            pass

        self.Player.stop()

    def fetchAndPlay(self, index):

        song = self.dba.fetchByIndex(index)
        self.play(song[0])

    def playlist(self):

        songs = self.dba.fetchPlayList()
        print "****************************** Play List ******************************"
        print "TOTAL: %s" % len(songs)
        for i, song in enumerate(songs):
            print str(i) + ".- " + song[0]
        for song in songs:
            self.play(song[0])

    def default(self, arg):
        print args


class Commands:

    SEARCH = "search"
    PLAY = "play"
    PLAYLIST = "playlist"
    message = "\n\nTerminado... Gracias por reproducir con PyMp3!\n"

class ConsoleProxy:

    Player = ConsolePlayer()

    def __init__(self, args):

        if args[0].lower() == Commands.SEARCH:
            self.Player.search(args[1])

        elif args[0].lower() == Commands.PLAY:
            try:
                index = int(args[1])
                self.Player.fetchAndPlay(index)
            except:
                self.Player.play(args[1])

        elif args[0].lower() == Commands.PLAYLIST:
            if len(args) == 2:
                self.Player.playlist(args[1])
            else:
                self.Player.playlist()

        else:
            self.Player.default(args)





