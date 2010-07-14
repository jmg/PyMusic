# -*- coding: utf-8 -*-
class mp3Tags:

    def __init__(self, mp3):
        self.mp3 = mp3
        try:        
            f = open(mp3, 'rb')
            f.seek(-128, 2)
            self.data = f.read()
            f.close()
        except:
            print "Archivo no valido"

    def titulo(self):
        try:
            titulo = self.data[3:33].replace('\00','').decode('utf-8')
            return self.isValid(titulo)
        except:
            return "Desconocido"
        
    def artista(self):
        try:
            artista = self.data[33:63].replace('\00','').decode('utf-8')
            return self.isValid(artista)
        except:
            return "Desconocido"

    def album(self):
        try:
            album = self.data[63:93].replace('\00','').decode('utf-8')
            return self.isValid(album)
        except:
            return "Desconocido"

    def year(self):
        try:
            year = self.data[93:97].replace('\00','').decode('utf-8')
            return self.isValidYear(year)
        except:
            return "-"
    
    
    def isValid(self,string):
        if string.count("U") > 3 or len(string) == 0 or string.isspace():
            return "Desconocido"
        return string
        
    def isValidYear(self,string):
        if string.count("U") > 3 or len(string) == 0 or string.isspace():
            return "-"
        return string
    
    #def comentarios(self):
    #    return self.data[97:126].replace('\00','')

    #def genero(self):
    #    return self.data[127:128].replace('\00','')
    
    def list(self):
        return [self.artista(),self.album(),self.year()]
