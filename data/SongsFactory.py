from pysqlite2 import dbapi2 as sqlite
from clases.clases import Song
import data.utils as utils

class SongsFactory():

    def __init__(self):
        self.conection = sqlite.connect('database/MusicaInYou.db')
        self.query = self.conection.cursor()

    def _make_object(self, *args):
        song = Song(*args)
        return song

    def _make_objects(self, rows):
        objetcs = []
        for row in rows:
            obj = self._make_object(*row)
            objetcs.append(obj)
        return objetcs

    def createTable(self):
        sintax = "CREATE TABLE if not exists songs (\
                  id       INTEGER PRIMARY KEY AUTOINCREMENT ,\
                   song     varchar(300) not null, \
                   interpret    varchar(100), \
                    album     varchar(100), \
                    year       varchar(10) \
                   )"
        self.query.execute(sintax)

    def insert(self, song):
        try:
            sintax = "select * from songs where song = \"" + song.path + "\""
            self.query.execute(sintax)
            print sintax
            if not self.query.fetchone():
                sintax = "insert into songs ('song', 'interpret', 'album', 'year') values \
                 (\"" + song.path + "\", \"" + song.artist + "\", \"" + song.album + "\" , \"" + song.year + "\" )"
                print sintax
                self.query.execute(sintax)
        except Exception, e:
            print e.message
        self.conection.commit()

    def fetch_one(self):
        sintax = "select song, interpret, album, year, id from songs order by song"
        self.query.execute(sintax)
        song = self.query.fetchone()
        return self._make_object(song)

    def fetch_all(self):
        sintax = "select id, song, interpret, album, year from songs order by song"
        self.query.execute(sintax)
        songs = self.query.fetchall()
        return self._make_objects(songs)

    def fetch_many(self, condition):
        sintax = "select id, song, interpret, album, year from songs where \
                    song like '%" + condition + "%' \
                    or interpret like '%" + condition + "%' \
                    or album like '%" + condition + "%' \
                    order by song \
                    "
        self.query.execute(sintax)
        songs = self.query.fetchall()
        return self._make_objects(songs)

    def delete(self, song):
        sintax = 'delete from songs where song = "' + song + '"'
        self.query.execute(sintax)
        self.conection.commit()

    def list_dir(self, dir):
        list = utils.list_dir(dir)
        print list
        objects = self._make_objects(list)
        return objects


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

    def fetch_all_scores(self):
        sintax = "select song,score from songs inner join \
                scores on scores.idsong = songs.id order by score desc"
        self.query.execute(sintax)
        return self.query.fetchall()



