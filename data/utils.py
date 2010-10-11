import os
from logic.tags import Tags
validFormats = ['.mp3','.wav','.wma']

#lista un directorio recursivamente
def list_dir(dir):
    list = []
    listSongs = []
    os.chdir(dir)
    list = os.popen("ls -1R").readlines()
    subdir = ""
    for name in list:
        name.replace(":\n","")
        name.replace("\n","")
        if name.find("./") == -1:
            if isValidFormat(name):
                if subdir:
                    directory = (dir + "/" + subdir + "/" + name).replace("\n","")
                    tags = getTags(directory)
                    tags.insert(0,directory)
                    tags.insert(0, 0)
                    listSongs.append(tags)
                else:
                    directory = (dir + "/" + name).replace("\n","")
                    tags = getTags(directory)
                    tags.insert(0,directory)
                    tags.insert(0, 0)
                    listSongs.append(tags)
        else:
            subdir = name.replace("./", "")
            subdir = subdir.replace(":\n", "")
            subdir = subdir.replace("\n", "")
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
