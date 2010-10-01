# -*- coding: utf-8 -*-

class BaseObject(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Song(BaseObject):

    def __init__(self, id='', path='', artist='', album='', year=''):
        self.id = id
        self.path = path
        self.artist = artist
        self.album = album
        self.year = year


class Radio(BaseObject):

    def __init__(self, id='', path='', artist='', album='', year=''):
        self.id = id
        self.path = path
        self.artist = artist
        self.album = album
        self.year = year

