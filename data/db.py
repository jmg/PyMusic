# -*- coding: utf-8 -*-
import sqlite3

from data.clases.clases import Song  # noqa: F401  (kept for backward compatibility)


class dataBase:

    validFormats = ['.mp3', '.wav', '.wma']

    def __init__(self):
        self.conection = sqlite3.connect('database/MusicaInYou.db')
        self.query = self.conection.cursor()

    # DBA para armar listas aleatorias

    def fetchRandomSongs(self, condition):
        sintax = """select song, interpret, album, year, id from songs where
                    song like ?
                    or interpret like ?
                    or album like ?
                    order by random()"""
        like = f"%{condition}%"
        self.query.execute(sintax, (like, like, like))
        return self.query.fetchall()

    def fetchOrderByScore(self, condition):
        sintax = """select song, interpret, album, year, score from songs
                    inner join scores on scores.idSong = songs.id where
                    song like ?
                    or interpret like ?
                    or album like ?
                    order by score"""
        like = f"%{condition}%"
        self.query.execute(sintax, (like, like, like))
        return self.query.fetchall()

    # DBA para puntuacion de temas

    def createTablePunctuation(self):
        sintax = """CREATE TABLE if not exists scores (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    idSong  int,
                    score   int
                   )"""
        self.query.execute(sintax)

    def fetchById(self, id):
        sintax = "select id from songs where id = ?"
        self.query.execute(sintax, (id,))

    # dba para los indices

    def createIndexTable(self):
        sintax = """CREATE TABLE if not exists IndexSongs (
                    idSong          int,
                    indexSong       int,
                    currentlyList   int
                   )"""
        self.query.execute(sintax)

    def UpdateIndex(self, idSong, index):
        self.query.execute(
            "select 1 from IndexSongs where indexSong = ?", (index,))
        if not self.query.fetchone():
            self.query.execute(
                "insert into IndexSongs (idSong, indexSong, currentlyList) values (?, ?, 1)",
                (idSong, index))
        else:
            self.query.execute(
                "update IndexSongs set idSong = ? where indexSong = ?",
                (idSong, index))
        self.conection.commit()

    def ResetList(self):
        self.query.execute("update IndexSongs set currentlyList = 0")
        self.conection.commit()

    def UpdateList(self, top):
        self.query.execute(
            "update IndexSongs set currentlyList = 1 where indexSong <= ?",
            (top,))
        self.conection.commit()

    def fetchByIndex(self, index):
        sintax = """select song from songs inner join IndexSongs
                    on songs.id = IndexSongs.idSong
                    where IndexSongs.indexSong = ?"""
        self.query.execute(sintax, (index,))
        return self.query.fetchone()

    def fetchManyWithId(self, condition):
        sintax = """select id, song, interpret, album, year, id from songs where
                    song like ?
                    or interpret like ?
                    or album like ?
                    order by song"""
        like = f"%{condition}%"
        self.query.execute(sintax, (like, like, like))
        return self.query.fetchall()

    def fetchPlayList(self):
        sintax = """select song from songs inner join IndexSongs on
                    songs.id = IndexSongs.idSong where IndexSongs.currentlyList = 1"""
        self.query.execute(sintax)
        return self.query.fetchall()

    def closeConection(self):
        self.conection.close()

    def __del__(self):
        try:
            self.conection.close()
        except Exception:
            pass
