import os
from logic.tags import Tags
validFormats = ['.mp3','.wav','.wma', '.avi', '.ogg']

def list_dir(root):
    """
        recursive list a of a dir
    """
    list = []
    listSongs = []

    for root, sub_folders, files in os.walk(root):
        for file in files:
            if isValidFormat(file):
                path = os.path.join(root, file)
                tags = getTags(path)
                tags.insert(0, path)
                tags.insert(0, 0)
                listSongs.append(tags)

    return listSongs


def isValidFormat(name):
        for format in validFormats:
            if name.find(format) != -1:
                return True
        return False

def getTags(song):
    #obtiene las tags del mp3
    mp3tags = Tags(song)
    return mp3tags.list()
