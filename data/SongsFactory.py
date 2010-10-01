from pysqlite2 import dbapi2 as sqlite
from clases.clases import Song
import data.utils as utils

class SongsFactory():

    validFormats = ['.mp3','.wav','.wma']

    def _make_object(self, *args):
        song = Song(*args)
        return song

    def _make_objects(self, rows):
        objetcs = []
        for row in rows:
            obj = self._make_object(*row)
            objetcs.append(obj)
        return objetcs

    def __init__(self):
        self.conection = sqlite.connect('database/MusicaInYou.db')
        self.query = self.conection.cursor()

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
        for song in listsongs:
            try:
                sintax = "select * from songs where song = \"" + song.path + "\""
                self.query.execute(sintax)
                if not self.query.fetchone():
                    sintax = "insert into songs ('song', 'interpret', 'album', 'year') values \
                     (\"" + song.path + "\", \"" + song.artist + "\", \"" + song.album + "\" , \"" + song.year + "\" )"
                    self.query.execute(sintax)
            except Exception, e:
                print e.message
        self.conection.commit()

    def fetchSong(self):
        sintax = "select song, interpret, album, year, id from songs order by song"
        self.query.execute(sintax)
        song = self.query.fetchone()
        return self._make_object(song)

    def fetchSongs(self):
        sintax = "select id, song, interpret, album, year from songs order by song"
        self.query.execute(sintax)
        songs = self.query.fetchall()
        return self._make_objects(songs)

    def fetchMany(self, condition):
        sintax = "select id, song, interpret, album, year from songs where \
                    song like '%" + condition + "%' \
                    or interpret like '%" + condition + "%' \
                    or album like '%" + condition + "%' \
                    order by song \
                    "
        self.query.execute(sintax)
        songs = self.query.fetchall()
        return self._make_objects(songs)

    def list_dir(self, dir):
        return self._make_objects(utils.list_dir(dir))



