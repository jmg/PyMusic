# -*- coding: utf-8 -*-
class Tags:

    def __init__(self, mp3):
        self.mp3 = mp3
        self.data = b""
        try:
            with open(mp3, 'rb') as f:
                f.seek(-128, 2)
                self.data = f.read()
        except (OSError, ValueError):
            print("Archivo no valido")

    def _decode(self, raw):
        return raw.replace(b'\x00', b'').decode('utf-8', errors='replace')

    def titulo(self):
        try:
            return self.isValid(self._decode(self.data[3:33]))
        except Exception:
            return "Desconocido"

    def artista(self):
        try:
            return self.isValid(self._decode(self.data[33:63]))
        except Exception:
            return "Desconocido"

    def album(self):
        try:
            return self.isValid(self._decode(self.data[63:93]))
        except Exception:
            return "Desconocido"

    def year(self):
        try:
            return self.isValidYear(self._decode(self.data[93:97]))
        except Exception:
            return "-"

    def isValid(self, string):
        if string.count("U") > 3 or len(string) == 0 or string.isspace():
            return "Desconocido"
        return string

    def isValidYear(self, string):
        if string.count("U") > 3 or len(string) == 0 or string.isspace():
            return "-"
        return string

    def list(self):
        return [self.artista(), self.album(), self.year()]
