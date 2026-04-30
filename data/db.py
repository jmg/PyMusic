# -*- coding: utf-8 -*-
"""Search and play-list/score helpers backed by the shared SQLAlchemy engine.

This module used to wrap a raw ``pysqlite2`` connection. It now goes through
the same ``alchemy.database`` engine as :mod:`alchemy.factory`, which means
every consumer talks to a single connection pool and the ORM-managed schema.
"""

from sqlalchemy import text

from alchemy.database import engine, init_db


class dataBase:

    validFormats = ['.mp3', '.wav', '.wma']

    def __init__(self):
        # Make sure the tables exist before any helper runs.
        init_db()

    # ------------------------------------------------------------------
    # Search helpers
    # ------------------------------------------------------------------
    def fetchRandomSongs(self, condition):
        sql = text("""
            select song, interpret, album, year, id from Songs where
            song like :pat or interpret like :pat or album like :pat
            order by random()
        """)
        with engine.connect() as conn:
            return list(conn.execute(sql, {"pat": f"%{condition}%"}))

    def fetchOrderByScore(self, condition):
        sql = text("""
            select song, interpret, album, year, score from Songs
            inner join scores on scores.idSong = Songs.id where
            song like :pat or interpret like :pat or album like :pat
            order by score
        """)
        with engine.connect() as conn:
            return list(conn.execute(sql, {"pat": f"%{condition}%"}))

    def fetchManyWithId(self, condition):
        sql = text("""
            select id, song, interpret, album, year, id from Songs where
            song like :pat or interpret like :pat or album like :pat
            order by song
        """)
        with engine.connect() as conn:
            return list(conn.execute(sql, {"pat": f"%{condition}%"}))

    # ------------------------------------------------------------------
    # Scores
    # ------------------------------------------------------------------
    def createTablePunctuation(self):
        # Schema is owned by alchemy.model.Score; init_db() handles creation.
        init_db()

    def scoreSong(self, idSong, score):
        with engine.begin() as conn:
            existing = conn.execute(
                text("select 1 from scores where idSong = :id"),
                {"id": idSong},
            ).fetchone()
            if existing:
                conn.execute(
                    text("update scores set score = :s where idSong = :id"),
                    {"s": score, "id": idSong},
                )
            else:
                conn.execute(
                    text("insert into scores (idSong, score) values (:id, :s)"),
                    {"id": idSong, "s": score},
                )

    def fetchById(self, id):
        sql = text("select id from Songs where id = :id")
        with engine.connect() as conn:
            return conn.execute(sql, {"id": id}).fetchone()

    # ------------------------------------------------------------------
    # Index / playlist tracking
    # ------------------------------------------------------------------
    def createIndexTable(self):
        init_db()

    def UpdateIndex(self, idSong, index):
        with engine.begin() as conn:
            existing = conn.execute(
                text("select 1 from IndexSongs where indexSong = :idx"),
                {"idx": index},
            ).fetchone()
            if existing:
                conn.execute(
                    text("update IndexSongs set idSong = :s where indexSong = :idx"),
                    {"s": idSong, "idx": index},
                )
            else:
                conn.execute(
                    text("""insert into IndexSongs
                            (idSong, indexSong, currentlyList)
                            values (:s, :idx, 1)"""),
                    {"s": idSong, "idx": index},
                )

    def ResetList(self):
        with engine.begin() as conn:
            conn.execute(text("update IndexSongs set currentlyList = 0"))

    def UpdateList(self, top):
        with engine.begin() as conn:
            conn.execute(
                text("update IndexSongs set currentlyList = 1 where indexSong <= :t"),
                {"t": top},
            )

    def fetchByIndex(self, index):
        sql = text("""
            select song from Songs inner join IndexSongs
            on Songs.id = IndexSongs.idSong
            where IndexSongs.indexSong = :idx
        """)
        with engine.connect() as conn:
            return conn.execute(sql, {"idx": index}).fetchone()

    def fetchPlayList(self):
        sql = text("""
            select song from Songs inner join IndexSongs on
            Songs.id = IndexSongs.idSong where IndexSongs.currentlyList = 1
        """)
        with engine.connect() as conn:
            return list(conn.execute(sql))

    def closeConection(self):
        # Kept for backwards compatibility; the engine owns the pool now.
        engine.dispose()

    def __del__(self):
        # Engine disposal is handled at process exit by SQLAlchemy itself.
        pass
