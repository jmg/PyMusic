import wxversion
wxversion.select("2.8")

from GUI import LyricReader
from wx import App
from terra import LyricsTerra

class pyLyricReader(LyricReader):

    def __init__(self, parent):
        LyricReader.__init__(self, parent)

    def tbTema_change(self, event):
        #enter key
        if event.GetKeyCode() == 13:
            self.do_search()
        else:
            event.Skip()

    def tbArtista_change(self, event):
        #enter key
        if event.GetKeyCode() == 13:
            self.do_search()
        else:
            event.Skip()

    def btBuscar_click( self, event ):
        self.do_search()

    def do_search(self):
        artist = self.tbArtista.GetValue()
        song = self.tbTema.GetValue()

        lyrics = LyricsTerra(song, artist)
        self.tbLyric.SetValue(lyrics.parse_lyrics())


if __name__ == "__main__":

    app = App(0)
    frame = pyLyricReader(None)
    frame.Show()
    app.MainLoop()
