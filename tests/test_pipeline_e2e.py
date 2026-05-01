"""End-to-end pipeline test.

Builds a fake music tree on disk, runs ``utils.list_dir`` to scan it, ingests
the result through ``PlayerDataLogic`` (the same path the wxGui uses when the
user clicks *Add List*) and reads everything back through both the SQLAlchemy
factories and the raw ``dataBase`` helper.
"""

import os

import pytest


def test_full_disk_to_database_roundtrip(isolated_db, fake_mp3, tmp_path):
    library = tmp_path / 'library'
    fake_mp3('rock/song-a.mp3', parent=library, artist='Anita',
             album='Pelo Suelto', year='2018')
    fake_mp3('rock/song-b.mp3', parent=library, artist='Anita',
             album='Pelo Suelto', year='2018')
    fake_mp3('jazz/song-c.mp3', parent=library, artist='Bilbao Trio',
             album='Madrugada', year='2020')
    # Non-audio files must be ignored by ``utils.list_dir``.
    (library / 'rock' / 'cover.jpg').write_bytes(b'\xff\xd8\xff')
    (library / 'readme.txt').write_text('not music')

    from data import utils
    listing = utils.list_dir(str(library))
    assert len(listing) == 3
    # Every entry is shaped as ``[None, path, artist, album, year]``.
    for entry in listing:
        assert entry[0] is None
        assert entry[1].endswith('.mp3')
        assert entry[2] in ('Anita', 'Bilbao Trio')

    from logic.player_logic import PlayerDataLogic
    pdl = PlayerDataLogic()
    pdl.createTable()

    songs = pdl.list_dir(str(library))
    assert {s.artist for s in songs} == {'Anita', 'Bilbao Trio'}
    pdl.add_songs(songs)

    # Read-back via the SQLAlchemy factory (used by the GUI).
    fetched = sorted(pdl.fetch_all_songs(), key=lambda s: s.path)
    assert len(fetched) == 3
    assert all(s.path.endswith('.mp3') for s in fetched)
    assert {s.album for s in fetched} == {'Pelo Suelto', 'Madrugada'}

    # Search uses LIKE under the hood.
    matches = pdl.find('Bilbao')
    assert len(matches) == 1
    assert matches[0].artist == 'Bilbao Trio'

    # Read-back via the raw helper (used by the console).
    from data.db import dataBase
    db = dataBase()
    rows = db.fetchManyWithId('Anita')
    assert len(rows) == 2
    paths = sorted(row[1] for row in rows)
    assert all('rock' in p for p in paths)


def test_radio_lifecycle(isolated_db):
    """Add → list → delete radios via the same factory the GUI uses."""
    from logic.player_logic import PlayerDataLogic

    pdl = PlayerDataLogic()
    pdl.create_table_radios()

    pdl.add_radio('http://stream.example.com/one')
    pdl.add_radio('http://stream.example.com/two')
    radios = pdl.fetch_radios()
    paths = sorted(r.path for r in radios)
    assert paths == [
        'http://stream.example.com/one',
        'http://stream.example.com/two',
    ]

    target = next(r for r in radios if r.path.endswith('one'))
    pdl.delete_radio(target.id)

    remaining = pdl.fetch_radios()
    assert [r.path for r in remaining] == ['http://stream.example.com/two']


def test_score_lifecycle_via_data_logic_and_db(isolated_db):
    """Insert songs, score one of them, fetch the score back through both
    APIs and make sure they agree."""
    from data.clases.clases import Song
    from data.SongsFactory import SongsFactory
    from data.db import dataBase
    from alchemy.database import init_db

    init_db()
    sf = SongsFactory()
    sf.createTable()
    sf.insert(Song(id=None, path='/m/song-a.mp3', artist='A', album='X', year='2020'))
    sf.insert(Song(id=None, path='/m/song-b.mp3', artist='B', album='Y', year='2021'))

    db = dataBase()
    rows = db.fetchManyWithId('')
    a_id = next(r[0] for r in rows if r[1].endswith('song-a.mp3'))

    db.scoreSong(a_id, 5)
    db.scoreSong(a_id, 9)  # update path

    scored = sf.fetch_all_scores()
    paths = [r[0] for r in scored]
    scores = [r[1] for r in scored]
    assert '/m/song-a.mp3' in paths
    assert 9 in scores  # the latest score wins
