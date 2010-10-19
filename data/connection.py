from pysqlite2 import dbapi2 as sqlite
from config import connection_string

def connected(f):
    """
        A new connection to the database
    """
    def wrapper(self, *args):
        self.conection = sqlite.connect(connection_string)
        self.query = self.conection.cursor()
        return f(self, *args)

    return wrapper
