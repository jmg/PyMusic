from pysqlite2 import dbapi2 as sqlite
from clases.clases import Radio

class RadiosFactory(object):

    def __init__(self):
        self.conection = sqlite.connect('database/MusicaInYou.db')
        self.query = self.conection.cursor()

    def _make_object(self, *args):
        radio = Radio(*args)
        return radio

    def _make_objects(self, rows):
        objetcs = []
        for row in rows:
            obj = self._make_object(*row)
            objetcs.append(obj)
        return objetcs

    def create_table(self):
        sintax = "CREATE TABLE if not exists radios (\
                  id       INTEGER PRIMARY KEY AUTOINCREMENT ,\
                   radio     varchar(300) not null, \
                   interpret    varchar(100), \
                    album     varchar(100), \
                    year       varchar(10) \
                   )"
        self.query.execute(sintax)

    def insert(self, radio):
        sintax = "insert into radios ('radio', 'interpret', 'album', 'year') values \
        (\""+ radio +"\", \""+ str(None) +"\", \""+ str(None) +"\" , \""+ str(None) +"\" )"
        self.query.execute(sintax)
        self.conection.commit()

    def fetch_all(self):
        sintax = "select id, radio, interpret, album, year from radios order by id"
        self.query.execute(sintax)
        radios = self.query.fetchall()
        return self._make_objects(radios)