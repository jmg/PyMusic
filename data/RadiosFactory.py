from data.clases.clases import Radio
from data.connection import connected


class RadiosFactory:

    def _make_object(self, *args):
        return Radio(*args)

    def _make_objects(self, rows):
        return [self._make_object(*row) for row in rows]

    @connected
    def create_table(self):
        sintax = """CREATE TABLE if not exists radios (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT ,
                    radio       varchar(300) not null,
                    interpret   varchar(100),
                    album       varchar(100),
                    year        varchar(10)
                   )"""
        self.query.execute(sintax)

    @connected
    def insert(self, radio):
        self.query.execute(
            "INSERT INTO radios (radio, interpret, album, year) values (?, ?, ?, ?)",
            (radio, "", "", ""))
        self.conection.commit()

    @connected
    def fetch_all(self):
        self.query.execute(
            "select id, radio, interpret, album, year from radios order by id")
        return self._make_objects(self.query.fetchall())

    @connected
    def delete(self, id):
        self.query.execute("DELETE from radios where id = ?", (id,))
        self.conection.commit()
