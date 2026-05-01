"""ID3v1 tag-reader (`logic.tags.Tags`) end-to-end tests."""

import pytest

from logic.tags import Tags


def test_id3v1_parses_artist_album_year(fake_mp3):
    path = fake_mp3('a.mp3', title='Mi Tema', artist='Mi Artista',
                    album='Mi Album', year='2024')

    t = Tags(str(path))
    assert t.artista() == 'Mi Artista'
    assert t.album() == 'Mi Album'
    assert t.year() == '2024'
    # ``list()`` is what data.utils.list_dir consumes
    assert t.list() == ['Mi Artista', 'Mi Album', '2024']


def test_id3v1_with_unicode(fake_mp3):
    path = fake_mp3('u.mp3', artist='Daníel', album='Año Cero', year='2020')
    t = Tags(str(path))
    assert t.artista() == 'Daníel'
    assert t.album() == 'Año Cero'


def test_missing_file_returns_unknown(tmp_path):
    t = Tags(str(tmp_path / 'no-such-file.mp3'))
    assert t.artista() == 'Desconocido'
    assert t.album() == 'Desconocido'
    assert t.year() == '-'


def test_blank_tag_returns_unknown(fake_mp3):
    """A whitespace-only tag value should map to 'Desconocido'."""
    path = fake_mp3('blank.mp3', artist=' ' * 20, album=' ' * 20, year='   ')
    t = Tags(str(path))
    assert t.artista() == 'Desconocido'
    assert t.album() == 'Desconocido'
    assert t.year() == '-'


def test_tail_too_short_does_not_crash(tmp_path):
    """File shorter than 128 bytes still produces a Tags object."""
    p = tmp_path / 'short.mp3'
    p.write_bytes(b'too short')
    # ``Tags.__init__`` swallows the seek error; subsequent calls return
    # the placeholders.
    t = Tags(str(p))
    assert t.artista() in ('Desconocido', '')
    assert t.year() in ('-', '')
