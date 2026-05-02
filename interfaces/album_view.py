"""Album-grid view: scrollable wrap of album cards (cover + title + artist).

Each card click filters the main playlist to the songs of that album.
"""

import io
import os
from collections import OrderedDict

import wx

from logic.tags import Tags


CARD_W = 160
CARD_H = 200
COVER_SIZE = 140
PLACEHOLDER_BG = wx.Colour(40, 40, 60)


class AlbumView(wx.ScrolledWindow):

    def __init__(self, parent, on_album_click=None):
        super().__init__(parent, style=wx.VSCROLL)
        self.SetScrollRate(0, 20)
        self.SetBackgroundColour(wx.Colour(20, 20, 32))

        self.on_album_click = on_album_click or (lambda artist, album: None)
        self.sizer = wx.WrapSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)

        self._cards = []

    # ------------------------------------------------------------------
    def populate(self, songs):
        # Group by (artist, album); pick the first song with a cover.
        groups = OrderedDict()
        for s in songs:
            key = (s.artist or "Desconocido", s.album or "Desconocido")
            groups.setdefault(key, []).append(s)

        # Clear existing cards
        for card in self._cards:
            self.sizer.Detach(card)
            card.Destroy()
        self._cards = []

        # "All Songs" reset card at the top of the grid.
        all_card = AlbumCard(
            self, "", "All Songs", None, sum(len(v) for v in groups.values()),
            lambda a, al: self.on_album_click("__ALL__", "__ALL__"),
        )
        self.sizer.Add(all_card, 0, wx.ALL, 8)
        self._cards.append(all_card)

        for (artist, album), tracks in groups.items():
            cover = self._find_cover(tracks)
            card = AlbumCard(self, artist, album, cover, len(tracks),
                             self._on_card_click)
            self.sizer.Add(card, 0, wx.ALL, 8)
            self._cards.append(card)

        self.Layout()
        self.FitInside()

    def _find_cover(self, tracks):
        for t in tracks:
            if not t.path or not os.path.exists(t.path):
                continue
            try:
                cb = Tags(t.path).cover()
                if cb:
                    return cb
            except Exception:
                continue
        return None

    def _on_card_click(self, artist, album):
        self.on_album_click(artist, album)


class AlbumCard(wx.Panel):

    def __init__(self, parent, artist, album, cover_bytes, track_count, click_cb):
        super().__init__(parent, size=(CARD_W, CARD_H))
        self.SetBackgroundColour(wx.Colour(28, 28, 42))
        self.artist = artist
        self.album = album
        self.click_cb = click_cb

        sz = wx.BoxSizer(wx.VERTICAL)

        bmp = self._build_bitmap(cover_bytes)
        self.bm = wx.StaticBitmap(self, bitmap=bmp, size=(COVER_SIZE, COVER_SIZE))
        sz.Add(self.bm, 0, wx.ALIGN_CENTER | wx.TOP, 6)

        title = wx.StaticText(self, label=self._truncate(album, 22))
        font = title.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        title.SetForegroundColour(wx.Colour(240, 240, 250))
        sz.Add(title, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 4)

        sub_text = f"{self._truncate(artist, 22)}  ·  {track_count}"
        sub = wx.StaticText(self, label=sub_text)
        sub.SetForegroundColour(wx.Colour(170, 170, 200))
        sz.Add(sub, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT | wx.BOTTOM, 4)

        self.SetSizer(sz)

        # Make every child clickable.
        for w in (self, self.bm, title, sub):
            w.Bind(wx.EVT_LEFT_DOWN, self._on_click)
            w.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def _build_bitmap(self, cover_bytes):
        if cover_bytes:
            try:
                stream = io.BytesIO(cover_bytes)
                img = wx.Image(stream)
                if img.IsOk():
                    img = img.Scale(COVER_SIZE, COVER_SIZE, wx.IMAGE_QUALITY_HIGH)
                    return wx.Bitmap(img)
            except Exception:
                pass
        # Placeholder
        bmp = wx.Bitmap(COVER_SIZE, COVER_SIZE)
        dc = wx.MemoryDC(bmp)
        dc.SetBackground(wx.Brush(PLACEHOLDER_BG))
        dc.Clear()
        dc.SetTextForeground(wx.Colour(120, 120, 160))
        font = dc.GetFont()
        font.SetPointSize(font.GetPointSize() + 6)
        dc.SetFont(font)
        text = "♪"
        tw, th = dc.GetTextExtent(text)
        dc.DrawText(text, (COVER_SIZE - tw) // 2, (COVER_SIZE - th) // 2)
        del dc
        return bmp

    @staticmethod
    def _truncate(s, n):
        s = s or ""
        return s if len(s) <= n else s[: n - 1] + "…"

    def _on_click(self, event):
        self.click_cb(self.artist, self.album)
