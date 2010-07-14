# -*- coding: utf-8 -*-
import gst

uri = "file:///home/jm/Música/02 - Kingdom.mp3"

player = gst.element_factory_make("playbin", "player")
    
print uri
player.set_property('uri', uri)
player.set_state(gst.STATE_PLAYING)

while 1:
    pass
