# -*- coding: utf-8 -*-
from pysqlite2 import dbapi2 as sqlite
import os
import dircache
import tags
import threading
import cache
import time
import pickle

class dataBase(threading.Thread):

    validFormats = ['.mp3','.wav','.wma']

    def __init__(self):
        threading.Thread.__init__(self)
        #/home/jm/Documentos/PyMp3/
        self.conection = sqlite.connect('MusicaInYou.db')
        self.query = self.conection.cursor()
        self.cache = cache.Cache()

    #DBA Para la Musica

    def createTable(self):
        sintax = "CREATE TABLE if not exists songs (\
                  id       INTEGER PRIMARY KEY AUTOINCREMENT ,\
                   song     varchar(300) not null, \
                   interpret    varchar(100), \
                    album     varchar(100), \
                    year       varchar(10) \
                   )"
        self.query.execute(sintax)

    def insert_songs(self, listsongs):
        for tag in listsongs:
            try:
                sintax = "select * from songs where song = \"" + tag[0] + "\""
                self.query.execute(sintax)
                if not self.query.fetchone():
                    sintax = "insert into songs ('song', 'interpret', 'album', 'year') values \
                     (\""+ tag[0] +"\", \""+ tag[1] +"\", \""+ tag[2] +"\" , \""+ tag[3] +"\" )"
                    self.query.execute(sintax)
            except:
                print tag[0],tag[1],tag[2],tag[3]
        self.conection.commit()

    def fetchSong(self):
        sintax = "select song, interpret, album, year, id from songs order by song"
        self.query.execute(sintax)
        return self.query.fetchone()

    def fetchSongs(self):
        sintax = "select song, interpret, album, year, id from songs order by song"
        self.query.execute(sintax)
        songs = self.query.fetchall()
        return songs

    #lista un directorio recursivamente
    def listDir(self, dir):
        list = []
        listSongs = []
        os.chdir(dir)
        list = os.popen("ls -1R").readlines()
        subdir = ""
        for name in list:
            name.replace(":\n","")
            name.replace("\n","")
            if name.find("./") == -1:
                if self.isValidFormat(name):
                    if subdir:
                        directory = (dir + "/" + subdir + "/" + name).replace("\n","")
                        tags = self.getTags(directory)
                        tags.insert(0,directory)
                        listSongs.append(tags)
                    else:
                        directory = (dir + "/" + name).replace("\n","")
                        tags = self.getTags(directory)
                        tags.insert(0,directory)
                        listSongs.append(tags)
            else:
                subdir = name.replace("./", "")
                subdir = subdir.replace(":\n", "")
                subdir = subdir.replace("\n", "")
        return listSongs

    def isValidFormat(self,name):
        for format in self.validFormats:
            if name.find(format) != -1:
                return True
        return False

    def getTags(self, song):
        #obtiene las tags del mp3
        mp3tags = tags.mp3Tags(song)
        return mp3tags.list()

    def fetchMany(self, condition):
        sintax = "select song, interpret, album, year, id from songs where \
                    song like '%" + condition + "%' \
                    or interpret like '%" + condition + "%' \
                    or album like '%" + condition + "%' \
                    order by song \
                    "
        songs = self.query.execute(sintax)
        #t1 = time.time()
        #songs = self.query.fetchManyWithId("")
        #t2 = time.time()
        #songs = pickle.dumps(songs)
        #self.cache.mc.set_multi(dict(zip(songs[0], songs)))
        return songs.fetchall()

    #DBA para las radios

    def createTableRadios(self):
        sintax = "CREATE TABLE if not exists radios (\
                  id       INTEGER PRIMARY KEY AUTOINCREMENT ,\
                   radio     varchar(300) not null, \
                   interpret    varchar(100), \
                    album     varchar(100), \
                    year       varchar(10) \
                   )"
        self.query.execute(sintax)

    def insertRadio(self, radio):
        sintax = "insert into radios ('radio', 'interpret', 'album', 'year') values \
        (\""+ radio +"\", \""+ str(None) +"\", \""+ str(None) +"\" , \""+ str(None) +"\" )"
        self.query.execute(sintax)
        self.conection.commit()

    def fetchRadios(self):
        sintax = "select radio, interpret, album, year, id from radios order by id"
        self.query.execute(sintax)
        return self.query.fetchall()


    #DBA para armar listas aleatorias

    def fetchRandomSongs(self, condition):
        sintax = "select song, interpret, album, year, id from songs where \
                    song like '%" + condition + "%' \
                    or interpret like '%" + condition + "%' \
                    or album like '%" + condition + "%' \
                    order by random()"
        self.query.execute(sintax)
        return self.query.fetchall()

    def fetchOrderByScore(self, condition):
        sintax = "select song, interpret, album, year, score from songs \
                    inner join scores on scores.idSong = songs.id where \
                    song like '%" + condition + "%' \
                    or interpret like '%" + condition + "%' \
                    or album like '%" + condition + "%' \
                    order by score"
        self.query.execute(sintax)
        return self.query.fetchall()

    def deleteSong(self, song):
        sintax = 'delete from songs where song = "' + song + '"'
        self.query.execute(sintax)
        print sintax

    #DBA para puntuacion de temas

    def createTablePunctuation(self):
        sintax = "CREATE TABLE if not exists scores (\
                  id       INTEGER PRIMARY KEY AUTOINCREMENT ,\
                   idSong   int , \
                   score   int  \
                   )"
        self.query.execute(sintax)

    def fetchById(self, id):
        sintax = "select id from songs where"
        self.query.execute(sintax)

    def scoreSong(self, idSong, score):
        sintax = "select * from scores where idSong = " + idSong
        self.query.execute(sintax)
        if not self.query.fetchone():
            print "new score!" , score
            sintax = "insert into scores (idSong, score) values  \
            (" + str(idSong) + "," + str(score) + ")"
            self.query.execute(sintax)
        else:
            sintax = "update scores set score = " + str(score) + " \
            where idSong = " + str(idSong)
            self.query.execute(sintax)
        self.conection.commit()

    def fetchSongsScores(self):
        sintax = "select song,score from songs inner join \
                scores on scores.idsong = songs.id order by score desc"
        self.query.execute(sintax)
        return self.query.fetchall()

    #dba para los indices

    def createIndexTable(self):
        sintax = "CREATE TABLE if not exists IndexSongs (\
                  idSong       int ,\
                   indexSong       int, \
                   currentlyList   int \
                   )"
        self.query.execute(sintax)

    def UpdateIndex(self, idSong, index):
        sintax = "select (1) from IndexSongs where IndexSong = " + str(index)
        self.query.execute(sintax)
        if not self.query.fetchone():
            sintax = "insert into IndexSongs (idSong, indexSong, currentlyList) values \
            (" + str(idSong) + "," + str(index) + ", 1)"
        else:
            sintax = "update IndexSongs set idSong = " + str(idSong) + " \
            where indexSong = " + str(index)
        self.query.execute(sintax)
        self.conection.commit()

    def ResetList(self):
        sintax = "update IndexSongs set currentlyList = 0"
        self.query.execute(sintax)
        self.conection.commit()

    def UpdateList(self, top):
        sintax = "update IndexSongs set currentlyList = 1 where indexSong <= %s" % (top)
        self.query.execute(sintax)
        self.conection.commit()

    def fetchByIndex(self, index):
        sintax = "select song from songs inner join IndexSongs \
        on songs.id = IndexSongs.idSong where \
        IndexSongs.IndexSong = %s" % index
        self.query.execute(sintax)
        return self.query.fetchone()

    def fetchManyWithId(self, condition):
        sintax = "select id, song, interpret, album, year, id from songs where \
                    song like '%" + condition + "%' \
                    or interpret like '%" + condition + "%' \
                    or album like '%" + condition + "%' \
                    order by song \
                    "
        self.query.execute(sintax)
        return self.query.fetchall()

    def fetchPlayList(self):
        sintax = "select song from songs inner join IndexSongs on \
        songs.id = IndexSongs.idSong where IndexSongs.currentlyList = 1"
        self.query.execute(sintax)
        songs = self.query.fetchall()
        return

    def closeConection(self):
        self.conection.close()

    def __del__(self):
        self.conection.close()



