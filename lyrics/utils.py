import re
from htmlentitydefs import name2codepoint

class EspecialChars(object):

    pattern = re.compile("&(#?\w+?);")

    @classmethod
    def _replace_entity(self, match):
        text = match.group(1)
        if text[0] == u'#':
            text = text[1:]
            try:
                if text[0] in u'xX':
                    c = int(text[1:], 16)
                else:
                    c = int(text)
                return unichr(c)
            except ValueError:
                return match.group(0)
        else:
            try:
                return unichr(name2codepoint[text])
            except (ValueError, KeyError):
                return match.group(0)

    @classmethod
    def unescape_entities(self, text):
        return self.pattern.sub(self._replace_entity, text)
