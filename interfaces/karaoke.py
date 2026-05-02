"""Karaoke pane: full-screen synced lyrics view.

Shows the previous, current, and next LRC lines. The current line is
big and centered; the others fade. Closes on Esc or Ctrl+K.
"""

import wx


class KaraokeFrame(wx.Frame):

    BG = wx.Colour(8, 8, 16)
    FG_PREV = wx.Colour(140, 140, 170)
    FG_CUR = wx.Colour(255, 255, 255)
    FG_NEXT = wx.Colour(180, 180, 210)
    FG_DIM = wx.Colour(80, 80, 110)

    def __init__(self, parent):
        super().__init__(parent, title="PyMusic — Karaoke",
                         style=wx.DEFAULT_FRAME_STYLE)
        self.parent_frame = parent
        self.SetBackgroundColour(self.BG)
        self.SetSize(wx.Size(1100, 600))
        self.Centre()

        self.Bind(wx.EVT_PAINT, self._on_paint)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, lambda e: self.Refresh(), self.timer)
        self.timer.Start(150)

        self.Bind(wx.EVT_CLOSE, self._on_close)

    def _on_close(self, event):
        try:
            self.timer.Stop()
        except Exception:
            pass
        try:
            self.parent_frame._karaoke_frame = None
        except Exception:
            pass
        self.Destroy()

    def _on_char(self, event):
        kc = event.GetKeyCode()
        if kc == wx.WXK_ESCAPE or (kc == ord('K') and event.ControlDown()):
            self.Close()
        elif kc == wx.WXK_F11:
            self.ShowFullScreen(not self.IsFullScreen())
        else:
            event.Skip()

    def _on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        gc = wx.GraphicsContext.Create(dc)
        if gc is None:
            return

        w, h = self.GetClientSize()
        gc.SetBrush(gc.CreateLinearGradientBrush(
            0, 0, 0, h, self.BG, wx.Colour(20, 20, 40),
        ))
        gc.DrawRectangle(0, 0, w, h)

        synced = getattr(self.parent_frame, "_synced_lyrics", []) or []
        if not synced:
            self._draw_centered(gc, w, h, "(no synced lyrics)", 28, self.FG_DIM)
            return

        try:
            pos_ns = self.parent_frame.logic.player.getSeekedPosition()
        except Exception:
            pos_ns = None
        pos_s = (pos_ns / 1_000_000_000) if pos_ns else 0

        idx = -1
        for i, (t, _) in enumerate(synced):
            if t <= pos_s:
                idx = i
            else:
                break

        prev_line = synced[idx - 1][1] if idx >= 1 else ""
        cur_line = synced[idx][1] if 0 <= idx < len(synced) else ""
        next_line = synced[idx + 1][1] if 0 <= idx + 1 < len(synced) else ""

        cy = h // 2
        self._draw_centered(gc, w, cy - 100, prev_line, 28, self.FG_PREV)
        self._draw_centered(gc, w, cy, cur_line, 56, self.FG_CUR, bold=True)
        self._draw_centered(gc, w, cy + 100, next_line, 28, self.FG_NEXT)

        # Song title at top
        meta = getattr(self.parent_frame, "_current_song_meta", None)
        if meta:
            song, artist = meta
            label = f"{song} — {artist}"
            self._draw_centered(gc, w, 40, label, 22, self.FG_DIM)

    def _draw_centered(self, gc, w, y, text, size, color, bold=False):
        if not text:
            return
        font = wx.Font(size, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                       wx.FONTWEIGHT_BOLD if bold else wx.FONTWEIGHT_NORMAL)
        gc.SetFont(font, color)
        tw, th = gc.GetTextExtent(text)
        gc.DrawText(text, max(20, (w - tw) / 2), y - th / 2)
