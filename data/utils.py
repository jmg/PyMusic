import os

from logic.tags import Tags

validFormats = ['.mp3', '.wav', '.wma', '.avi', '.ogg']


def list_dir(root):
    """Recursively list audio files inside ``root``."""
    listSongs = []

    for current_root, _sub_folders, files in os.walk(root):
        for file in files:
            if isValidFormat(file):
                path = os.path.join(current_root, file)
                tags = getTags(path)
                tags.insert(0, path)
                tags.insert(0, None)
                listSongs.append(tags)

    return listSongs


def isValidFormat(name):
    return any(name.find(fmt) != -1 for fmt in validFormats)


def getTags(song):
    return Tags(song).list()
