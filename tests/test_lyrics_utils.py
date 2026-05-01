"""HTML-entity un-escaping used by the lyrics parsers."""

from lyrics.utils import EspecialChars


def test_named_entity():
    assert EspecialChars.unescape_entities('caf&eacute;') == 'café'


def test_decimal_entity():
    assert EspecialChars.unescape_entities('&#233;') == 'é'


def test_hex_entity_lowercase():
    assert EspecialChars.unescape_entities('&#xe9;') == 'é'


def test_hex_entity_uppercase():
    assert EspecialChars.unescape_entities('&#xE9;') == 'é'


def test_unknown_entity_passes_through():
    assert EspecialChars.unescape_entities('&zzznotreal;') == '&zzznotreal;'


def test_mixed_text():
    src = 'Hello &amp; goodbye, caf&eacute;!'
    assert EspecialChars.unescape_entities(src) == 'Hello & goodbye, café!'


def test_terra_url_construction():
    """LyricsTerra builds the search URL without hitting the network."""
    from lyrics.terra import LyricsTerra
    lt = LyricsTerra('proud mary', 'creedence')
    assert lt.url == 'http://letras.terra.com.br/winamp.php?t=creedence-proud%20mary'
