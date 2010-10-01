# -*- coding: utf-8 -*-
from pysqlite2 import dbapi2 as sqlite
import os
from logic.tags import Tags
import threading
import time
import pickle

from data.clases.clases import Song

class dataBase():

    validFormats = ['.mp3','.wav','.wma']

    def __init__(self):
        self.conection = sqlite.connect('database/MusicaInYou.db')
        self.query = self.conection.cursor()

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



