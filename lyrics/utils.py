import re
from html.entities import name2codepoint


class EspecialChars:

    pattern = re.compile(r"&(#?\w+?);")

    @classmethod
    def _replace_entity(cls, match):
        text = match.group(1)
        if text[0] == '#':
            text = text[1:]
            try:
                if text[0] in 'xX':
                    c = int(text[1:], 16)
                else:
                    c = int(text)
                return chr(c)
            except ValueError:
                return match.group(0)
        else:
            try:
                return chr(name2codepoint[text])
            except (ValueError, KeyError):
                return match.group(0)

    @classmethod
    def unescape_entities(cls, text):
        return cls.pattern.sub(cls._replace_entity, text)
