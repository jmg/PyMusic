import sqlite3

from data.config import connection_string


def connected(f):
    """Open a fresh sqlite connection on the wrapped instance before delegating."""
    def wrapper(self, *args, **kwargs):
        self.conection = sqlite3.connect(connection_string)
        self.query = self.conection.cursor()
        return f(self, *args, **kwargs)

    return wrapper
