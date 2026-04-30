from data.clases.clases import Song
from data import utils
from data.connection import connected


class SongsFactory:

    def _make_object(self, *args):
        return Song(*args)

    def _make_objects(self, rows):
        return [self._make_object(*row) for row in rows]

    def list_dir(self, dir):
        list = utils.list_dir(dir)
        return self._make_objects(list)

    @connected
    def createTable(self):
        sintax = """CREATE TABLE if not exists songs (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT ,
                    song          varchar(300) not null,
                    interpret     varchar(100),
                    album         varchar(100),
                    year          varchar(10)
                   )"""
        self.query.execute(sintax)

    @connected
    def exists(self, song):
        try:
            self.query.execute(
                "SELECT 1 FROM songs WHERE song = ?", (song.path,))
            return self.query.fetchone() is not None
        except Exception as e:
            print(f"error en exists({song.path!r}): {e}")
            return True

    @connected
    def insert(self, song):
        if not self.exists(song):
            try:
                self.query.execute(
                    "INSERT INTO songs (song, interpret, album, year) VALUES (?, ?, ?, ?)",
                    (song.path, song.artist, song.album, song.year))
            except Exception as e:
                print(e)
            self.conection.commit()

    @connected
    def fetch_one(self):
        sintax = "select song, interpret, album, year, id from songs order by song"
        self.query.execute(sintax)
        song = self.query.fetchone()
        return self._make_object(song)

    @connected
    def fetch_all(self):
        sintax = "select id, song, interpret, album, year from songs order by song"
        self.query.execute(sintax)
        return self._make_objects(self.query.fetchall())

    @connected
    def fetch_many(self, condition):
        sintax = """SELECT id, song, interpret, album, year from songs where
                    song like ?
                    or interpret like ?
                    or album like ?
                    order by song"""
        like = f"%{condition}%"
        self.query.execute(sintax, (like, like, like))
        return self._make_objects(self.query.fetchall())

    @connected
    def delete(self, song):
        self.query.execute("delete from songs where id = ?", (song.id,))
        self.conection.commit()

    @connected
    def scoreSong(self, idSong, score):
        self.query.execute("select * from scores where idSong = ?", (idSong,))
        if not self.query.fetchone():
            self.query.execute(
                "insert into scores (idSong, score) values (?, ?)",
                (idSong, score))
        else:
            self.query.execute(
                "update scores set score = ? where idSong = ?",
                (score, idSong))
        self.conection.commit()

    @connected
    def fetch_all_scores(self):
        sintax = """select song, score from songs inner join
                    scores on scores.idsong = songs.id order by score desc"""
        self.query.execute(sintax)
        return self.query.fetchall()
