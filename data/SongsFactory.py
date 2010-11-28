from clases.clases import Song
import data.utils as utils
from connection import connected

class SongsFactory():

    def _make_object(self, *args):
        song = Song(*args)
        return song

    def _make_objects(self, rows):
        objetcs = []
        for row in rows:
            obj = self._make_object(*row)
            objetcs.append(obj)
        return objetcs

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
            sintax = """SELECT 1 FROM songs WHERE song = '%s' """ % song.path
            print sintax
            self.query.execute(sintax)
            return self.query.fetchone() is not None
        except:
            print "error en: " + str(sintax)
            return True

    @connected
    def insert(self, song):

        if not self.exists(song):
            try:
                sintax = """INSERT INTO songs ('song', 'interpret', 'album', 'year') VALUES
                    ('%s','%s','%s','%s')""" % (song.path, song.artist, song.album, song.year)

                self.query.execute(sintax)
            except Exception, e:
                print e.message
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
        songs = self.query.fetchall()
        return self._make_objects(songs)

    @connected
    def fetch_many(self, condition):
        sintax = """SELECT id, song, interpret, album, year from songs where
                    song like '%%%s%%'
                    or interpret like '%%%s%%'
                    or album like '%%%s%%'
                    order by song
                    """ % (condition, condition, condition)
        print sintax
        self.query.execute(sintax)
        songs = self.query.fetchall()
        return self._make_objects(songs)

    @connected
    def delete(self, song):
        sintax = "delete from songs where id = %s" % song.id
        self.query.execute(sintax)
        self.conection.commit()

    @connected
    def scoreSong(self, idSong, score):
        sintax = "select * from scores where idSong = " + idSong
        self.query.execute(sintax)
        if not self.query.fetchone():
            sintax = "insert into scores (idSong, score) values  \
            (" + str(idSong) + "," + str(score) + ")"
            self.query.execute(sintax)
        else:
            sintax = "update scores set score = " + str(score) + " \
            where idSong = " + str(idSong)
            self.query.execute(sintax)
        self.conection.commit()

    @connected
    def fetch_all_scores(self):
        sintax = "select song,score from songs inner join \
                scores on scores.idsong = songs.id order by score desc"
        self.query.execute(sintax)
        return self.query.fetchall()
